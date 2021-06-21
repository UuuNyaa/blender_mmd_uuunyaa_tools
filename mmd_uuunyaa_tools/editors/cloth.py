# -*- coding: utf-8 -*-
# Copyright 2021
#   小威廉伯爵 https://github.com/958261649/Miku_Miku_Rig
#   UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from typing import List, Union

import bmesh
import bpy
from mmd_uuunyaa_tools.m17n import _
from mmd_uuunyaa_tools.utilities import MessageException


class ConvertRigidBodyToClothOperator(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.convert_rigid_bodies_to_cloth'
    bl_label = _('Convert Rigid Bodies to Cloth')
    bl_options = {'REGISTER', 'UNDO'}

    subdivide: bpy.props.IntProperty(default=0, description=_('Subdivide level'), min=0, max=5)
    cloth_convert_mod: bpy.props.IntProperty(default=1, description=_('Cloth convert mode'), min=1, max=3)
    auto_select_mesh: bpy.props.BoolProperty(default=True, description=_('Auto select mesh'))
    auto_select_rigid_body: bpy.props.BoolProperty(default=True, description=_('Auto select rigid bodies'))

    def execute(self, context: bpy.types.Context):
        ClothEditor.convert_rigid_body_to_cloth(self.subdivide, self.cloth_convert_mod, self.auto_select_rigid_body, self.auto_select_mesh)
        return {'FINISHED'}


class ConvertRigidBodyToClothPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_mmd_converter'
    bl_label = _('UuuNyaa MMD Converter')
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'

    def draw(self, context: bpy.types.Context):
        self.layout.operator(ConvertRigidBodyToClothOperator.bl_idname)


class ClothEditor:
    @staticmethod
    def convert_rigid_body_to_cloth(subdivide: int, cloth_convert_mod: int, auto_select_rigid_body: bool, auto_select_mesh: bool):
        select_obj: List[bpy.types.Object] = bpy.context.selected_objects
        mmd_mesh: Union[bpy.types.Object, None] = None
        mmd_arm = None
        mmd_parent = None
        select_rigid_body: List[bpy.types.Object] = []
        select_mesh: List[bpy.types.Object] = []

        for obj in select_obj:
            if obj.type == 'MESH':
                for m in obj.modifiers:
                    if m.type == 'ARMATURE':
                        select_mesh.append(obj)
                        break
                if hasattr(obj, 'mmd_rigid'):
                    if obj.mmd_rigid.name != '':
                        select_rigid_body.append(obj)

        if len(select_rigid_body) == 0:
            raise MessageException(_('所选物体中没有MMD刚体'))

        if auto_select_rigid_body:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = select_rigid_body[0]
            bpy.ops.mmd_tools.rigid_body_select(properties={'collision_group_number'})  # pylint: disable=no-member
            rigid_bodies = bpy.context.selected_objects
        else:
            rigid_bodies = select_rigid_body

        mmd_parent = select_rigid_body[0].parent.parent

        if auto_select_mesh:
            obj: bpy.types.Object
            for obj in mmd_parent.children:
                if obj.type == 'ARMATURE':
                    mmd_arm = obj
                    mmd_mesh = mmd_arm.children[0]
            if mmd_mesh is None:
                raise MessageException(_('所选刚体没有对应网格模型'))
        elif len(select_mesh) == 0:
            raise MessageException(_('所选物体中没有MMD网格模型'))
        else:
            mmd_mesh = select_mesh[0]

        mmd_arm = mmd_mesh.parent

        rigid_bodys_count = len(rigid_bodies)
        joints = []
        side_joints = []
        edge_index = []
        verts = []
        edges = []
        bones_list: List[bpy.types.PoseBone] = []

        mean_radius = 0

        for rigid_body in rigid_bodies:
            if rigid_body.mmd_rigid.shape == 'BOX':
                radius = min(rigid_body.mmd_rigid.size[0], min(rigid_body.mmd_rigid.size[1], rigid_body.mmd_rigid.size[2]))
            else:
                radius = rigid_body.mmd_rigid.size[0]
            mean_radius += radius

            bone = mmd_arm.pose.bones[rigid_body.mmd_rigid.bone]
            verts.append(rigid_body.location)
            bones_list.append(bone)

        mean_radius /= rigid_bodys_count

        for obj in bpy.context.view_layer.objects:
            if not hasattr(obj, 'rigid_body_constraint'):
                continue

            if obj.rigid_body_constraint is not None:
                if obj.rigid_body_constraint.object1 in rigid_bodies and obj.rigid_body_constraint.object2 in rigid_bodies:
                    joints.append(obj)
                    index1 = rigid_bodies.index(obj.rigid_body_constraint.object1)
                    index2 = rigid_bodies.index(obj.rigid_body_constraint.object2)
                    edge_index.append([index1, index2])
                    edges.append([index1, index2])
                elif obj.rigid_body_constraint.object1 in rigid_bodies or obj.rigid_body_constraint.object2 in rigid_bodies:
                    side_joints.append(obj)

        mesh = bpy.data.meshes.new('mmd_cloth')
        mesh.from_pydata(verts, edges, [])
        mesh.validate()
        cloth_obj = bpy.data.objects.new('mmd_cloth', mesh)
        bpy.context.collection.objects.link(cloth_obj)
        cloth_obj.parent = mmd_parent
        bpy.ops.object.select_all(action='DESELECT')

        bpy.context.view_layer.objects.active = cloth_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.mode_set(mode='OBJECT')

        # 删除大于四边的面
        # remove ngon
        bm = bmesh.new()  # pylint: disable=assignment-from-no-return,invalid-name
        bm.from_mesh(mesh)
        for face in bm.faces:
            if len(face.verts) > 4:
                bm.faces.remove(face)

        # 删除多余边
        # remove extra edge
        for edge in bm.edges:
            true_edge = False
            for i in edge_index:
                if edge.verts[0].index in i and edge.verts[1].index in i:
                    true_edge = True
                    break

            if true_edge == False:
                bm.edges.remove(edge)

        # 尝试标记出头发,飘带
        # try mark hair or ribbon vertex
        bm.to_mesh(mesh)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False, use_multi_face=False, use_non_contiguous=False, use_verts=False)
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.object.mode_set(mode='OBJECT')
        bm.clear()
        bm.from_mesh(mesh)

        # 标记出特殊边和点
        # These are special edge and vertex
        hair_verts = []
        up_edges = []
        down_edges = []
        side_edges = []
        up_verts: List[bmesh.types.BMVert] = []
        down_verts: List[bmesh.types.BMVert] = []
        wire_verts: List[bmesh.types.BMVert] = []
        side_verts: List[bmesh.types.BMVert] = []

        # 标出头部，尾部，飘带顶点
        # try mark head,tail,ribbon vertex
        bm.verts.ensure_lookup_table()
        for i in range(len(bm.verts)):
            vertex = bm.verts[i]
            bone = bones_list[i]
            if bone.bone.use_connect == False:
                up_verts.append(vertex)
            elif len(bone.children) == 0:
                down_verts.append(vertex)
            elif bone.children[0] not in bones_list:
                down_verts.append(vertex)
            if vertex.is_wire:
                wire_verts.append(vertex)
            if vertex.select:
                hair_verts.append(vertex)
                if cloth_convert_mod == 1:
                    vertex.co = bone.tail
            if cloth_convert_mod == 2:
                vertex.co = bone.tail

        bm.edges.ensure_lookup_table()
        for i in range(len(bm.edges)):
            edge = bm.edges[i]
            vert1 = edge.verts[0]
            vert2 = edge.verts[1]
            if edge.is_boundary:
                if vert1 in up_verts and vert2 in up_verts:
                    up_edges.append(edge)
                elif vert1 in down_verts and vert2 in down_verts:
                    down_edges.append(edge)
                else:
                    side_edges.append(edge)
                    if edge.verts[0] not in side_verts:
                        side_verts.append(edge.verts[0])
                    if edge.verts[1] not in side_verts:
                        side_verts.append(edge.verts[1])

        # 延长头部顶点
        # extend root vertex
        new_up_verts = [None for i in range(len(bm.verts))]
        new_down_verts = [None for i in range(len(bm.verts))]
        for i in range(len(up_verts)):
            vertex = up_verts[i]
            new_location = bones_list[vertex.index].head
            if cloth_convert_mod == 1 and vertex not in hair_verts or cloth_convert_mod == 3:
                for edge in vertex.link_edges:
                    if edge not in up_edges:
                        if edge.verts[0] == vertex:
                            new_location = vertex.co*2-edge.verts[1].co
                        else:
                            new_location = vertex.co*2-edge.verts[0].co
                    break
            new_vert = bm.verts.new(new_location)
            new_edge = bm.edges.new([vertex, new_vert])
            new_up_verts[vertex.index] = new_vert
            if vertex in side_verts:
                side_verts.append(new_vert)
                side_edges.append(new_edge)
            bm.edges.ensure_lookup_table()

        # 延长尾部顶点
        # extend tail vertex
        for i in range(len(down_verts)):
            vertex = down_verts[i]
            if vertex not in up_verts:
                new_location = [0, 0, 0]
                for edge in vertex.link_edges:
                    if edge not in down_edges:
                        if edge.verts[0] == vertex:
                            new_location = vertex.co*2-edge.verts[1].co
                        else:
                            new_location = vertex.co*2-edge.verts[0].co
                    break
                new_vert = bm.verts.new(new_location)
                new_edge = bm.edges.new([vertex, new_vert])
                new_down_verts[vertex.index] = new_vert
                if vertex in side_verts:
                    side_verts.append(new_vert)
                    side_edges.append(new_edge)
                bm.edges.ensure_lookup_table()

        for i in range(len(up_edges)):
            edge = up_edges[i]
            vert1 = edge.verts[0]
            vert2 = edge.verts[1]
            vert3 = new_up_verts[vert2.index]
            vert4 = new_up_verts[vert1.index]
            if vert3 is not None and vert4 is not None:
                bm.faces.new([vert1, vert2, vert3, vert4])
            bm.edges.ensure_lookup_table()

        for i in range(len(down_edges)):
            edge = down_edges[i]
            vert1 = edge.verts[0]
            vert2 = edge.verts[1]
            vert3 = new_down_verts[vert2.index]
            vert4 = new_down_verts[vert1.index]
            if vert3 is not None and vert4 is not None:
                bm.faces.new([vert1, vert2, vert3, vert4])
            bm.edges.ensure_lookup_table()

        bm.verts.index_update()
        bm.faces.ensure_lookup_table()
        new_side_verts = [None for i in range(len(bm.verts))]
        for i in range(len(side_verts)):
            vertex = side_verts[i]
            for edge in vertex.link_edges:
                if edge not in side_edges:
                    if edge.verts[0] == vertex:
                        new_location = vertex.co*2-edge.verts[1].co
                    else:
                        new_location = vertex.co*2-edge.verts[0].co
                    break
            new_vert = bm.verts.new(new_location)
            new_side_verts[vertex.index] = new_vert
            bm.edges.ensure_lookup_table()

        for i in range(len(side_edges)):
            edge = side_edges[i]
            vert1 = edge.verts[0]
            vert2 = edge.verts[1]
            vert3 = new_side_verts[vert2.index]
            vert4 = new_side_verts[vert1.index]
            if vert3 is not None and vert4 is not None:
                bm.faces.new([vert1, vert2, vert3, vert4])
            bm.edges.ensure_lookup_table()

        bm.verts.ensure_lookup_table()
        bm.to_mesh(mesh)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

        pin_vertex_group = cloth_obj.vertex_groups.new(name='mmd_cloth_pin')
        for obj in joints:
            bpy.data.objects.remove(obj)
        for obj in side_joints:
            if obj.rigid_body_constraint.object1 in rigid_bodies:
                side_rigid_body = obj.rigid_body_constraint.object1
                pin_rigid_body = obj.rigid_body_constraint.object2
            else:
                side_rigid_body = obj.rigid_body_constraint.object2
                pin_rigid_body = obj.rigid_body_constraint.object1

            index1 = rigid_bodies.index(side_rigid_body)
            vert2 = new_up_verts[index1]
            if vert2 is not None:
                index3 = vert2.index
                vert3 = new_side_verts[index3]
                if vert3 is None:
                    pin_index = [index3]
                else:
                    pin_index = [index3, vert3.index]
            else:
                pin_index = [index1]

            pin_bone_name = pin_rigid_body.mmd_rigid.bone

            skin_vertex_group = cloth_obj.vertex_groups.get(pin_bone_name)
            if skin_vertex_group is None:
                skin_vertex_group = cloth_obj.vertex_groups.new(name=pin_bone_name)
            skin_vertex_group.add(pin_index, 1, 'REPLACE')
            pin_vertex_group.add(pin_index, 1, 'REPLACE')
            bpy.data.objects.remove(obj)

        deform_vertex_group = mmd_mesh.vertex_groups.new(name='mmd_cloth_deform')

        cloth_obj.display_type = 'WIRE'

        mod = cloth_obj.modifiers.new('mmd_cloth_subsurface', 'SUBSURF')
        mod.levels = subdivide
        mod.render_levels = subdivide
        mod.boundary_smooth = 'PRESERVE_CORNERS'
        mod.show_only_control_edges = False

        mod = cloth_obj.modifiers.new('mmd_cloth_skin', 'ARMATURE')
        mod.object = mmd_arm
        mod.vertex_group = 'mmd_cloth_pin'

        mod = cloth_obj.modifiers.new('mmd_cloth', 'CLOTH')
        mod.settings.vertex_group_mass = 'mmd_cloth_pin'

        mod = cloth_obj.modifiers.new('mmd_cloth_smooth', 'CORRECTIVE_SMOOTH')
        mod.smooth_type = 'LENGTH_WEIGHTED'
        mod.rest_source = 'BIND'
        bpy.ops.object.correctivesmooth_bind(modifier='mmd_cloth_smooth')
        if subdivide == 0:
            mod.show_viewport = False

        bpy.context.view_layer.objects.active = mmd_mesh

        for i in range(rigid_bodys_count):
            vertex = bm.verts[i]
            obj = rigid_bodies[i]
            bone = bones_list[i]
            name = bone.name
            if vertex in hair_verts and cloth_convert_mod == 1 or cloth_convert_mod == 2:
                line_vertex_group = cloth_obj.vertex_groups.new(name=name)
                line_vertex_group.add([i], 1, 'REPLACE')
                for c in bone.constraints:
                    bone.constraints.remove(c)
                con = bone.constraints.new(type='STRETCH_TO')
                con.target = cloth_obj
                con.subtarget = name
                con.rest_length = bone.length
            else:
                mod = mmd_mesh.modifiers.new('combin_weight', 'VERTEX_WEIGHT_MIX')
                mod.vertex_group_a = deform_vertex_group.name
                mod.vertex_group_b = name
                mod.mix_set = 'OR'
                mod.mix_mode = 'ADD'
                mod.normalize = False
                bpy.ops.object.modifier_move_to_index(modifier='combin_weight', index=0)  # pylint: disable=no-member
                bpy.ops.object.modifier_apply(modifier='combin_weight')
                mmd_mesh.vertex_groups.remove(mmd_mesh.vertex_groups[name])
            bpy.data.objects.remove(obj)

        # 挤出孤立边
        bpy.context.view_layer.objects.active = cloth_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False, use_multi_face=False, use_non_contiguous=False, use_verts=False)
        bpy.ops.mesh.extrude_edges_move(TRANSFORM_OT_translate={'value': (0, 0.01, 0)})
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.transform.shrink_fatten(value=mean_radius, use_even_offset=False, mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

        bpy.ops.object.mode_set(mode='OBJECT')

        if len(mesh.polygons.items()) != 0 and cloth_convert_mod != 2:
            bpy.context.view_layer.objects.active = mmd_mesh
            mod = mmd_mesh.modifiers.new('mmd_cloth_deform', 'SURFACE_DEFORM')
            mod.target = cloth_obj
            mod.vertex_group = deform_vertex_group.name
            bpy.ops.object.surfacedeform_bind(modifier=mod.name)

        bm.free()

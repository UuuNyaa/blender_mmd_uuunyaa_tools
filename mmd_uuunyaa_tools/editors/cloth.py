# -*- coding: utf-8 -*-
# Copyright 2021
#   小威廉伯爵 https://github.com/958261649/Miku_Miku_Rig
#   UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import time
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from inspect import currentframe, getframeinfo
from typing import Dict, Iterable, List, Set, Tuple, Union

import bmesh
import bpy
from mmd_uuunyaa_tools.m17n import _
from mmd_uuunyaa_tools.utilities import MessageException, import_mmd_tools

mmd_tools = import_mmd_tools()


class PhysicsMode(Enum):
    AUTO = 'Auto'
    BONE_CONSTRAINT = 'Bone Constraint'
    SURFACE_DEFORM = 'Surface Deform'


translation_properties = [
    _('Auto'),
    _('Bone Constraint'),
    _('Surface Deform'),
]


class ConvertRigidBodyToClothOperator(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.convert_rigid_bodies_to_cloth'
    bl_label = _('Convert Rigid Bodies to Cloth')
    bl_options = {'REGISTER', 'UNDO'}

    subdivision_level: bpy.props.IntProperty(default=0, name=_('Subdivision Level'), min=0, max=5)
    physics_mode: bpy.props.EnumProperty(
        name=_('Physics Mode'),
        items=[(m.name, m.value, '') for m in PhysicsMode],
        default=PhysicsMode.AUTO.name
    )

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return False

        selected_mesh_mmd_root = None
        selected_rigid_body_mmd_root = None

        mmd_find_root = mmd_tools.core.model.Model.findRoot
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                return False

            if obj.mmd_type == 'RIGID_BODY':
                selected_rigid_body_mmd_root = mmd_find_root(obj)
            elif obj.mmd_type == 'NONE':
                selected_mesh_mmd_root = mmd_find_root(obj)

            if selected_rigid_body_mmd_root == selected_mesh_mmd_root:
                return selected_rigid_body_mmd_root is not None

        return False

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: bpy.types.Context):

        mmd_find_root = mmd_tools.core.model.Model.findRoot

        target_root_object = None
        rigid_body_objects: List[bpy.types.Object] = []
        mesh_objects: List[bpy.types.Object] = []

        obj: bpy.types.Object
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            root_object = mmd_find_root(obj)
            if root_object is None:
                continue

            if target_root_object is None:
                target_root_object = root_object
            elif target_root_object != root_object:
                raise MessageException(_('Multiple MMD models selected. Please select single at a time.'))

            if obj.mmd_type == 'RIGID_BODY':
                rigid_body_objects.append(obj)
            elif obj.mmd_type == 'NONE':
                mesh_objects.append(obj)

        ClothEditor.convert_physics_rigid_body_to_cloth(
            target_root_object,
            rigid_body_objects,
            mesh_objects,
            self.subdivision_level,
            PhysicsMode[self.physics_mode]
        )
        return {'FINISHED'}


@dataclass
class Edges:
    up_edges: Set[bmesh.types.BMEdge] = field(default_factory=set)
    down_edges: Set[bmesh.types.BMEdge] = field(default_factory=set)
    side_edges: Set[bmesh.types.BMEdge] = field(default_factory=set)


@dataclass
class Vertices:
    up_verts: Set[bmesh.types.BMVert] = field(default_factory=set)
    down_verts: Set[bmesh.types.BMVert] = field(default_factory=set)
    # wire_verts: Set[bmesh.types.BMVert] = field(default_factory=set)
    hair_verts: Set[bmesh.types.BMVert] = field(default_factory=set)
    side_verts: Set[bmesh.types.BMVert] = field(default_factory=set)


class UuuNyaaPhysicsPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_physics'
    bl_label = _('UuuNyaa Physics')
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'

    @classmethod
    def poll(cls, context):
        return mmd_tools.core.model.Model.findRoot(context.active_object)

    def draw(self, context: bpy.types.Context):
        root_object = mmd_tools.core.model.Model.findRoot(context.active_object)

        layout = self.layout
        col = layout.column()
        col.prop(root_object.mmd_root, 'show_rigid_bodies', text='Show All Rigid Bodies')
        col.operator_context = 'EXEC_DEFAULT'
        operator = col.operator('mmd_tools.rigid_body_select', text=_('Select Related Rigid Bodies'), icon='RESTRICT_SELECT_OFF')
        operator.properties = set(['collision_group_number', 'shape'])

        row = col.split(factor=0.9, align=True)
        row.operator_context = 'EXEC_DEFAULT'
        row.operator(ConvertRigidBodyToClothOperator.bl_idname, icon='MATCLOTH')
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator(ConvertRigidBodyToClothOperator.bl_idname, text=_(''), icon='WINDOW')


class MeshEditorABC(ABC):
    @staticmethod
    def add_modifier(mesh_object: bpy.types.Object, modifier_type: str, name: str, **kwargs) -> bpy.types.Modifier:
        modifier = mesh_object.modifiers.new(name, modifier_type)
        for key, value in kwargs.items():
            setattr(modifier, key, value)
        return modifier

    @classmethod
    def add_subsurface_modifier(cls, mesh_object: bpy.types.Object, name: str, levels: int, render_levels: int, **kwargs) -> bpy.types.Modifier:
        return cls.add_modifier(
            mesh_object, 'SUBSURF', name,
            levels=levels,
            render_levels=render_levels,
            boundary_smooth='PRESERVE_CORNERS',
            show_only_control_edges=False,
            **kwargs
        )

    @classmethod
    def add_armature_modifier(cls, mesh_object: bpy.types.Object, name: str, armature_object: bpy.types.Object, **kwargs) -> bpy.types.Modifier:
        return cls.add_modifier(
            mesh_object, 'ARMATURE', name,
            object=armature_object,
            **kwargs
        )

    @classmethod
    def add_cloth_modifier(cls, mesh_object: bpy.types.Object, name: str, **kwargs) -> bpy.types.Modifier:
        return cls.add_modifier(
            mesh_object, 'CLOTH', name,
            **kwargs
        )

    @classmethod
    def add_corrective_smooth_modifier(cls, mesh_object: bpy.types.Object, name: str, **kwargs) -> bpy.types.Modifier:
        return cls.add_modifier(
            mesh_object, 'CORRECTIVE_SMOOTH', name,
            **kwargs
        )

    @classmethod
    def add_surface_deform_modifier(cls, mesh_object: bpy.types.Object, name: str, **kwargs) -> bpy.types.Modifier:
        return cls.add_modifier(
            mesh_object, 'SURFACE_DEFORM', name,
            **kwargs
        )


class ClothEditor(MeshEditorABC):
    @classmethod
    def convert_physics_rigid_body_to_cloth(
        cls,
        root_object: bpy.types.Object,
        rigid_body_objects: List[bpy.types.Object],
        mesh_objects: List[bpy.types.Object],
        subdivision_level: int,
        physics_mode: PhysicsMode
    ):

        mmd_model = mmd_tools.core.model.Model(root_object)
        mmd_mesh_object = mesh_objects[0]
        mmd_armature_object = mmd_model.armature()

        rigid_bodys_count = len(rigid_body_objects)
        rigid_body_index_dict = {
            rigid_body_objects[i]: i
            for i in range(rigid_bodys_count)
        }

        pose_bones: List[bpy.types.PoseBone] = [mmd_armature_object.pose.bones[r.mmd_rigid.bone] for r in rigid_body_objects]

        rigid_body_mean_radius: float = sum([
            min(r.mmd_rigid.size) if r.mmd_rigid.shape == 'BOX'
            else r.mmd_rigid.size[0]
            for r in rigid_body_objects
        ]) / rigid_bodys_count

        def remove_objects(objects: Iterable[bpy.types.Object]):
            for obj in objects:
                bpy.data.objects.remove(obj)

        joint_objects, joint_edge_indices, side_joint_objects = cls.collect_joints(mmd_model, rigid_body_index_dict)

        remove_objects(joint_objects)

        cloth_mesh = bpy.data.meshes.new('mmd_uuunyaa_physics_cloth')
        cloth_mesh.from_pydata([r.location for r in rigid_body_objects], joint_edge_indices, [])
        cloth_mesh.validate()

        cloth_mesh_object = cls.new_mesh_object('mmd_uuunyaa_physics_cloth', cloth_mesh)
        cloth_mesh_object.parent = mmd_armature_object
        cloth_mesh_object.display_type = 'WIRE'

        cls.add_edge_faces(cloth_mesh_object)
        cls.clean_mesh(cloth_mesh, joint_edge_indices)

        cls.select_hair_ribbon_vertices(cloth_mesh_object)

        # 标记出特殊边和点
        # These are special edge and vertex
        cloth_bm: bmesh.types.BMesh = bmesh.new()
        cloth_bm.from_mesh(cloth_mesh)

        # 标出头部，尾部，飘带顶点
        # try mark head,tail,ribbon vertex
        cloth_bm.verts.ensure_lookup_table()
        cloth_bm.edges.ensure_lookup_table()

        vertices = cls.collect_vertices(cloth_bm, pose_bones, physics_mode)
        edges = cls.collect_edges(cloth_bm, vertices)

        new_up_verts = cls.extend_up_mesh(cloth_bm, pose_bones, vertices, edges, physics_mode)
        new_down_verts = cls.extend_down_mesh(cloth_bm, vertices, edges)

        cloth_bm.verts.index_update()

        cls.fill_faces(cloth_bm, edges.up_edges, new_up_verts)
        cls.fill_faces(cloth_bm, edges.down_edges, new_down_verts)

        cloth_bm.verts.index_update()

        new_side_verts = cls.extend_mesh_side(cloth_bm, vertices, edges)

        cls.fill_faces(cloth_bm, edges.side_edges, new_side_verts)

        cloth_bm.edges.ensure_lookup_table()
        cloth_bm.verts.ensure_lookup_table()
        cloth_bm.to_mesh(cloth_mesh)

        cls.normals_make_consistent(cloth_mesh_object)

        pin_vertex_group = cls.new_pin_vertex_group(cloth_mesh_object, side_joint_objects, new_up_verts, new_side_verts, rigid_body_index_dict)

        remove_objects(side_joint_objects)

        deform_vertex_group: bpy.types.VertexGroup = mmd_mesh_object.vertex_groups.new(name='mmd_uuunyaa_physics_cloth_deform')

        cls.add_subsurface_modifier(cloth_mesh_object, 'mmd_uuunyaa_physics_cloth_subsurface', subdivision_level, subdivision_level)
        cls.add_armature_modifier(cloth_mesh_object, 'mmd_uuunyaa_physics_cloth_armature', mmd_armature_object, vertex_group=pin_vertex_group.name)
        cloth_modifier = cls.add_cloth_modifier(cloth_mesh_object, 'mmd_uuunyaa_physics_cloth')
        cloth_modifier.settings.vertex_group_mass = pin_vertex_group.name

        corrective_smooth_modifier = cls.add_corrective_smooth_modifier(cloth_mesh_object, 'mmd_uuunyaa_physics_cloth_smooth', smooth_type='LENGTH_WEIGHTED', rest_source='BIND')
        bpy.ops.object.correctivesmooth_bind(modifier=corrective_smooth_modifier.name)
        if subdivision_level == 0:
            corrective_smooth_modifier.show_viewport = False

        deform_vertex_group_index = deform_vertex_group.index
        vertices_hair_verts = vertices.hair_verts

        cls.bind_mmd_mesh(mmd_mesh_object, cloth_mesh_object, cloth_bm, pose_bones, deform_vertex_group_index, vertices_hair_verts, physics_mode)

        remove_objects(rigid_body_objects)

        cls.fix_mesh(cloth_mesh_object, rigid_body_mean_radius)

        if len(cloth_mesh.polygons) != 0 and physics_mode in {PhysicsMode.AUTO, PhysicsMode.SURFACE_DEFORM}:
            bpy.context.view_layer.objects.active = mmd_mesh_object
            bpy.ops.object.surfacedeform_bind(
                modifier=cls.add_surface_deform_modifier(
                    mmd_mesh_object, 'mmd_uuunyaa_physics_cloth_deform',
                    target=cloth_mesh_object,
                    vertex_group=deform_vertex_group.name
                ).name
            )

        cloth_bm.free()

    @staticmethod
    def fix_mesh(cloth_mesh_object: bpy.types.Object, radius: float):
        # 挤出孤立边
        bpy.context.view_layer.objects.active = cloth_mesh_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False, use_multi_face=False, use_non_contiguous=False, use_verts=False)
        bpy.ops.mesh.extrude_edges_move(TRANSFORM_OT_translate={'value': (0, 0.01, 0)})
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.transform.shrink_fatten(value=radius, use_even_offset=False, mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def bind_mmd_mesh(mmd_mesh_object, cloth_mesh_object, cloth_bm, pose_bones, deform_vertex_group_index, vertices_hair_verts, physics_mode):
        unnecessary_vertex_groups: List[bpy.types.VertexGroup] = []

        mmd_mesh: bpy.types.Mesh = mmd_mesh_object.data
        mmd_bm: bmesh.types.BMesh = bmesh.new()
        mmd_bm.from_mesh(mmd_mesh)

        mmd_bm.verts.layers.deform.verify()
        deform_layer = mmd_bm.verts.layers.deform.active

        for i, bone in enumerate(pose_bones):
            vert = cloth_bm.verts[i]
            name = bone.name
            if vert in vertices_hair_verts and physics_mode in {PhysicsMode.AUTO, PhysicsMode.BONE_CONSTRAINT}:
                line_vertex_group = cloth_mesh_object.vertex_groups.new(name=name)
                line_vertex_group.add([i], 1, 'REPLACE')
                for c in bone.constraints:
                    bone.constraints.remove(c)
                con = bone.constraints.new(type='STRETCH_TO')
                con.target = cloth_mesh_object
                con.subtarget = name
                con.rest_length = 0.0
            else:
                # merge deform vertex weights
                from_vertex_group = mmd_mesh_object.vertex_groups[name]
                from_index = from_vertex_group.index
                unnecessary_vertex_groups.append(from_vertex_group)

                vert: bmesh.types.BMVert
                for vert in mmd_bm.verts:
                    deform_vert: bmesh.types.BMDeformVert = vert[deform_layer]
                    if from_index not in deform_vert:
                        continue

                    to_index = deform_vertex_group_index
                    deform_vert[to_index] = deform_vert.get(to_index, 0.0) + deform_vert[from_index]

        mmd_bm.to_mesh(mmd_mesh)
        mmd_bm.free()

        for vertex_group in unnecessary_vertex_groups:
            mmd_mesh_object.vertex_groups.remove(vertex_group)

    @staticmethod
    def new_pin_vertex_group(cloth_mesh_object, side_joint_objects, new_up_verts, new_side_verts, rigid_body_index_dict):
        pin_vertex_group = cloth_mesh_object.vertex_groups.new(name='mmd_uuunyaa_physics_cloth_pin')

        for obj in side_joint_objects:
            if obj.rigid_body_constraint.object1 in rigid_body_index_dict:
                side_rigid_body = obj.rigid_body_constraint.object1
                pin_rigid_body = obj.rigid_body_constraint.object2
            else:
                side_rigid_body = obj.rigid_body_constraint.object2
                pin_rigid_body = obj.rigid_body_constraint.object1

            index1 = rigid_body_index_dict[side_rigid_body]
            vert2 = new_up_verts[index1]
            if vert2 is None:
                pin_index = [index1]
            else:
                vert3 = new_side_verts[vert2.index]
                if vert3 is None:
                    pin_index = [vert2.index]
                else:
                    pin_index = [vert2.index, vert3.index]

            pin_bone_name = pin_rigid_body.mmd_rigid.bone

            skin_vertex_group = cloth_mesh_object.vertex_groups.get(pin_bone_name)
            if skin_vertex_group is None:
                skin_vertex_group = cloth_mesh_object.vertex_groups.new(name=pin_bone_name)

            skin_vertex_group.add(pin_index, 1, 'REPLACE')
            pin_vertex_group.add(pin_index, 1, 'REPLACE')

        return pin_vertex_group

    @staticmethod
    def normals_make_consistent(cloth_mesh_object):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = cloth_mesh_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def extend_mesh_side(cloth_bm, vertices, edges):
        new_side_verts = [None for i in range(len(cloth_bm.verts))]

        for vert in vertices.side_verts:
            for edge in vert.link_edges:
                if edge not in edges.side_edges:
                    if edge.verts[0] == vert:
                        new_location = vert.co*2-edge.verts[1].co
                    else:
                        new_location = vert.co*2-edge.verts[0].co
                    break
            new_vert = cloth_bm.verts.new(new_location)
            new_side_verts[vert.index] = new_vert

        return new_side_verts

    @staticmethod
    def fill_faces(cloth_bm, edges, new_verts):
        for edge in edges:
            vert1 = edge.verts[0]
            vert2 = edge.verts[1]
            vert3 = new_verts[vert2.index]
            vert4 = new_verts[vert1.index]

            if vert3 is not None and vert4 is not None:
                cloth_bm.faces.new([vert1, vert2, vert3, vert4])

    @staticmethod
    def extend_up_mesh(cloth_bm, pose_bones: List[bpy.types.PoseBone], vertices: Vertices, edges: Edges, physics_mode: PhysicsMode):
        new_up_verts = [None for i in range(len(cloth_bm.verts))]

        # 延长头部顶点
        # extend root vertex
        for vert in vertices.up_verts:
            new_location = pose_bones[vert.index].head

            if (
                (physics_mode == PhysicsMode.AUTO and vert not in vertices.hair_verts)
                or physics_mode == PhysicsMode.SURFACE_DEFORM
            ):
                for edge in vert.link_edges:
                    if edge in edges.up_edges:
                        break

                    if edge.verts[0] == vert:
                        new_location = vert.co*2-edge.verts[1].co
                    else:
                        new_location = vert.co*2-edge.verts[0].co

            new_vert = cloth_bm.verts.new(new_location)
            new_edge = cloth_bm.edges.new([vert, new_vert])
            new_up_verts[vert.index] = new_vert

            if vert in vertices.side_verts:
                vertices.side_verts.add(new_vert)
                edges.side_edges.add(new_edge)

        return new_up_verts

    @staticmethod
    def extend_down_mesh(cloth_bm, vertices: Vertices, edges: Edges):
        new_down_verts = [None for i in range(len(cloth_bm.verts))]
        # 延长尾部顶点
        # extend tail vertex
        for vert in vertices.down_verts:
            if vert in vertices.up_verts:
                continue

            new_location = [0, 0, 0]
            for edge in vert.link_edges:
                if edge in edges.down_edges:
                    break

                if edge.verts[0] == vert:
                    new_location = vert.co*2-edge.verts[1].co
                else:
                    new_location = vert.co*2-edge.verts[0].co

            new_vert = cloth_bm.verts.new(new_location)
            new_edge = cloth_bm.edges.new([vert, new_vert])
            new_down_verts[vert.index] = new_vert

            if vert in vertices.side_verts:
                vertices.side_verts.add(new_vert)
                edges.side_edges.add(new_edge)

        return new_down_verts

    @staticmethod
    def select_hair_ribbon_vertices(cloth_mesh_object: bpy.types.Object):
        # 尝试标记出头发,飘带
        # try mark hair or ribbon vertex
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = cloth_mesh_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=False, use_multi_face=False, use_non_contiguous=False, use_verts=False)
        bpy.ops.mesh.select_linked(delimit=set())
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def new_mesh_object(name: str, cloth_mesh: bpy.types.Mesh):
        cloth_mesh_object = bpy.data.objects.new(name, cloth_mesh)
        bpy.context.collection.objects.link(cloth_mesh_object)

        return cloth_mesh_object

    @staticmethod
    def add_edge_faces(cloth_mesh_object: bpy.types.Object):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = cloth_mesh_object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_face_add()
        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def collect_joints(mmd_model, rigid_body_index_dict: Dict[bpy.types.Object, int]) -> Tuple[List[bpy.types.Object], List[Tuple[int, int]], List[bpy.types.Object]]:
        joint_objects: List[bpy.types.Object] = []
        joint_edge_indices: List[Tuple[int, int]] = []
        side_joint_objects: List[bpy.types.Object] = []

        for obj in mmd_model.joints():
            obj1 = obj.rigid_body_constraint.object1
            obj2 = obj.rigid_body_constraint.object2
            if obj1 in rigid_body_index_dict and obj2 in rigid_body_index_dict:
                joint_objects.append(obj)
                joint_edge_indices.append((rigid_body_index_dict[obj1], rigid_body_index_dict[obj2]))
            elif obj1 in rigid_body_index_dict or obj2 in rigid_body_index_dict:
                side_joint_objects.append(obj)

        return joint_objects, joint_edge_indices, side_joint_objects

    @staticmethod
    def collect_vertices(cloth_bm: bmesh.types.BMesh, pose_bones: List[bpy.types.PoseBone], physics_mode: PhysicsMode) -> Vertices:
        vertices = Vertices()

        for i in range(len(cloth_bm.verts)):
            vert = cloth_bm.verts[i]
            bone = pose_bones[i]
            if not bone.bone.use_connect:
                vertices.up_verts.add(vert)
            elif len(bone.children) == 0:
                vertices.down_verts.add(vert)
            elif bone.children[0] not in pose_bones:
                vertices.down_verts.add(vert)

            # if vert.is_wire:
            #     vertices.wire_verts.add(vert)

            if vert.select:
                vertices.hair_verts.add(vert)
                if physics_mode == PhysicsMode.AUTO:
                    vert.co = bone.tail

            if physics_mode == PhysicsMode.BONE_CONSTRAINT:
                vert.co = bone.tail

        return vertices

    @staticmethod
    def collect_edges(cloth_bm: bmesh.types.BMesh, vertices: Vertices) -> Edges:
        edges = Edges()

        for edge in cloth_bm.edges:
            if not edge.is_boundary:
                continue

            vert1 = edge.verts[0]
            vert2 = edge.verts[1]
            if vert1 in vertices.up_verts and vert2 in vertices.up_verts:
                edges.up_edges.add(edge)
            elif vert1 in vertices.down_verts and vert2 in vertices.down_verts:
                edges.down_edges.add(edge)
            else:
                edges.side_edges.add(edge)
                if edge.verts[0] not in vertices.side_verts:
                    vertices.side_verts.add(edge.verts[0])
                if edge.verts[1] not in vertices.side_verts:
                    vertices.side_verts.add(edge.verts[1])
        return edges

    @staticmethod
    def clean_mesh(mesh: bpy.types.Mesh, save_edges: List[Tuple[int, int]]):
        def remove_ngon(cloth_bm):
            # 删除大于四边的面
            # remove ngon
            for face in cloth_bm.faces:
                if len(face.verts) > 4:
                    cloth_bm.faces.remove(face)

        def remove_edges(cloth_bm: bmesh.types.BMesh, save_edges):
            # 删除多余边
            # remove extra edge
            for edge in cloth_bm.edges:
                is_save_edge = False
                for i in save_edges:
                    if edge.verts[0].index in i and edge.verts[1].index in i:
                        is_save_edge = True
                        break

                if not is_save_edge:
                    cloth_bm.edges.remove(edge)

        cloth_bm = bmesh.new()  # pylint: disable=assignment-from-no-return,invalid-name
        cloth_bm.from_mesh(mesh)
        remove_ngon(cloth_bm)
        remove_edges(cloth_bm, save_edges)
        cloth_bm.to_mesh(mesh)
        cloth_bm.free()

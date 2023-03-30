# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import collections
import dataclasses
import itertools
from operator import itemgetter
import math
import random
from typing import Dict, List, Optional, Set, Tuple

import bmesh
import bpy
from mmd_uuunyaa_tools.m17n import _
from mmd_uuunyaa_tools.utilities import (import_mmd_tools,
                                         is_mmd_tools_installed,
                                         label_multiline)


class ConvertMaterialsForEevee(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.convert_materials_for_eevee'
    bl_label = _('Convert Materials for Eevee')
    bl_description = _('Convert materials of selected objects for Eevee.')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            next((x for x in context.selected_objects if x.type == 'MESH'), None)
            and is_mmd_tools_installed()
        )

    def execute(self, context):
        mmd_tools = import_mmd_tools()
        for obj in (x for x in context.selected_objects if x.type == 'MESH'):
            mmd_tools.cycles_converter.convertToCyclesShader(obj, use_principled=True, clean_nodes=True)

        if context.scene.render.engine != 'BLENDER_EEVEE':
            context.scene.render.engine = 'BLENDER_EEVEE'

        return {'FINISHED'}


class SetupRenderEngineForEevee(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.setup_render_engine_for_eevee'
    bl_label = _('Setup Render Engine for Eevee')
    bl_description = _('Setup render engine properties for Eevee.')
    bl_options = {'REGISTER', 'UNDO'}

    use_bloom: bpy.props.BoolProperty(name=_('Use Bloom'), default=True)
    use_motion_blur: bpy.props.BoolProperty(name=_('Use Motion Blur'), default=False)
    film_transparent: bpy.props.BoolProperty(name=_('Use Film Transparent'), default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if context.scene.render.engine != 'BLENDER_EEVEE':
            context.scene.render.engine = 'BLENDER_EEVEE'

        eevee = context.scene.eevee

        # Sampling
        # > Render: 8
        eevee.taa_render_samples = 16
        # > Viewport: 8
        eevee.taa_samples = 16

        # Ambient Occlusion: enable
        eevee.use_gtao = True
        # > Distance: 0.1 m
        eevee.gtao_distance = 0.100

        # Bloom: enable
        eevee.use_bloom = self.use_bloom
        if self.use_bloom:
            # > Threshold: 1.000
            eevee.bloom_threshold = 1.000
            # > Intensity: 0.100
            eevee.bloom_intensity = 0.100

        # Depth of Field
        # > Max Size: 16 px
        eevee.bokeh_max_size = 16.000

        # Screen Space Reflections: enable
        eevee.use_ssr = True
        # > Refrection: enable
        eevee.use_ssr_refraction = True
        # > Edge Fading: 0.000
        eevee.ssr_border_fade = 0.075

        # Motion Blur
        eevee.use_motion_blur = self.use_motion_blur

        # Shadows
        # > Cube Size 1024 px
        eevee.shadow_cube_size = '1024'
        # > Cascade Size 2048 px
        eevee.shadow_cascade_size = '2048'
        # > Soft Shadows: True
        eevee.use_soft_shadows = True

        # Indirect lighting: enable
        # > Irradiance Smoothing: 0.50
        eevee.gi_irradiance_smoothing = 0.50

        # Film > Transparent
        context.scene.render.film_transparent = self.film_transparent

        # Color Management
        # > View Transform: Filmic
        context.scene.view_settings.view_transform = 'Filmic'
        # > Look: High Contrast
        context.scene.view_settings.look = 'High Contrast'

        return {'FINISHED'}


class SetupRenderEngineForToonEevee(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.setup_render_engine_for_toon_eevee'
    bl_label = _('Setup Render Engine for Toon Eevee')
    bl_description = _('Setup render engine properties for Toon Eevee.')
    bl_options = {'REGISTER', 'UNDO'}

    use_bloom: bpy.props.BoolProperty(name=_('Use Bloom'), default=True)
    use_motion_blur: bpy.props.BoolProperty(name=_('Use Motion Blur'), default=False)
    use_soft_shadows: bpy.props.BoolProperty(name=_('Use Soft Shadows'), default=True)
    film_transparent: bpy.props.BoolProperty(name=_('Use Film Transparent'), default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if context.scene.render.engine != 'BLENDER_EEVEE':
            context.scene.render.engine = 'BLENDER_EEVEE'

        eevee = context.scene.eevee

        # Sampling
        # > Render: 8
        eevee.taa_render_samples = 8
        # > Viewport: 8
        eevee.taa_samples = 8

        # Ambient Occlusion: enable
        eevee.use_gtao = True
        # > Distance: 0.1 m
        eevee.gtao_distance = 0.100

        # Bloom: enable
        eevee.use_bloom = self.use_bloom
        if self.use_bloom:
            # > Threshold: 1.000
            eevee.bloom_threshold = 1.000
            # > Intensity: 0.100
            eevee.bloom_intensity = 0.100

        # Depth of Field
        # > Max Size: 16 px
        eevee.bokeh_max_size = 16.000

        # Screen Space Reflections: enable
        eevee.use_ssr = True
        # > Refrection: enable
        eevee.use_ssr_refraction = True
        # > Edge Fading: 0.000
        eevee.ssr_border_fade = 0.075

        # Motion Blur
        eevee.use_motion_blur = self.use_motion_blur

        # Shadows
        # > Cube Size 1024 px
        eevee.shadow_cube_size = '1024'
        # > Cascade Size 2048 px
        eevee.shadow_cascade_size = '2048'
        # > Soft Shadows
        eevee.use_soft_shadows = self.use_soft_shadows

        # Indirect lighting: enable
        # > Irradiance Smoothing: 0.50
        eevee.gi_irradiance_smoothing = 0.50

        # Film > Transparent
        context.scene.render.film_transparent = self.film_transparent

        # Color Management
        # > View Transform: Standard
        context.scene.view_settings.view_transform = 'Standard'
        # > Look: None
        context.scene.view_settings.look = 'None'

        return {'FINISHED'}


class SetupRenderEngineForWorkbench(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.setup_render_engine_for_workbench'
    bl_label = _('Setup Render Engine for Workbench')
    bl_description = _('Setup render engine properties for Workbench.')
    bl_options = {'REGISTER', 'UNDO'}

    use_shadow: bpy.props.BoolProperty(name=_('Use Shadow'), default=True)
    use_dof: bpy.props.BoolProperty(name=_('Use Depth of Field'), default=True)
    film_transparent: bpy.props.BoolProperty(name=_('Use Film Transparent'), default=False)

    @classmethod
    def poll(cls, _context):
        return True

    def execute(self, context: bpy.types.Context):
        if context.scene.render.engine != 'BLENDER_WORKBENCH':
            context.scene.render.engine = 'BLENDER_WORKBENCH'

        shading = context.scene.display.shading

        # Lighting: Flat
        shading.light = 'FLAT'

        # Color: Texture
        shading.color_type = 'TEXTURE'

        # Options
        # > Cavity: enable
        shading.show_cavity = self.use_shadow
        # > Type: World
        shading.cavity_type = 'WORLD'
        # > Ridge: 0.200
        shading.cavity_ridge_factor = 0.200
        # > Valley: 1.000
        shading.cavity_valley_factor = 1.000
        # > Depth of Field: enable
        shading.use_dof = self.use_dof

        # Film > Transparent
        context.scene.render.film_transparent = self.film_transparent

        # Color Management
        # > View Transform: Standard
        context.scene.view_settings.view_transform = 'Standard'
        # > Look: None
        context.scene.view_settings.look = 'None'

        return {'FINISHED'}


class ShowMessageBox(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.show_message_box'
    bl_label = _('Show Message Box')
    bl_options = {'INTERNAL'}

    icon: bpy.props.StringProperty(default='INFO')
    title: bpy.props.StringProperty(default='')
    message: bpy.props.StringProperty(default='')
    width: bpy.props.IntProperty(default=400)

    def execute(self, context):
        self.report({'INFO'}, message=self.message)
        return context.window_manager.invoke_popup(self, width=self.width)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.title, icon=self.icon)
        col = layout.column(align=True)
        label_multiline(col, text=self.message, width=self.width)


class RemoveUnusedVertexGroups(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.remove_unused_vertex_groups'
    bl_label = _('Remove Unused Vertex Groups')
    bl_description = _('Remove unused vertex groups from the active meshes')
    bl_options = {'REGISTER', 'UNDO'}

    weight_threshold: bpy.props.FloatProperty(name=_('Weight Threshold'), default=0.0, min=0.0, max=1.0)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: bpy.types.Context):
        # pylint: disable=too-many-branches
        obj: bpy.types.Object
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            used_vertex_group_indices: Set[int] = set()

            mesh: bpy.types.Mesh = obj.data

            # Used groups from weight paint
            vertex: bpy.types.MeshVertex
            for vertex in mesh.vertices:
                vertex_group: bpy.types.VertexGroupElement
                for vertex_group in vertex.groups:
                    if vertex_group.weight < self.weight_threshold:
                        continue

                    vertex_group_indices = vertex_group.group
                    used_vertex_group_indices.add(vertex_group_indices)

            vertex_groups = obj.vertex_groups

            # Used groups from modifiers
            for modifier in obj.modifiers:
                vertex_group = getattr(modifier, 'vertex_group', None)
                if not vertex_group:
                    continue

                if vertex_group not in vertex_groups:
                    continue

                vertex_group_index = vertex_groups[vertex_group].index
                used_vertex_group_indices.add(vertex_group_index)

            # Used groups from shape keys
            if mesh.shape_keys:
                key_block: bpy.types.ShapeKey
                for key_block in mesh.shape_keys.key_blocks:
                    if not key_block.vertex_group:
                        continue

                    vertex_group = vertex_groups.get(key_block.vertex_group)
                    if not vertex_group:
                        continue

                    used_vertex_group_indices.add(vertex_group.index)

            for vertex_group in list(reversed(vertex_groups)):
                if vertex_group.index in used_vertex_group_indices:
                    continue
                vertex_groups.remove(vertex_group)

        return {'FINISHED'}


class SelectShapeKeyTargetVertices(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.select_shape_key_target_vertices'
    bl_label = _('Select Shape Key Target Vertices')
    bl_description = _('Select shape key target vertices from the active meshes')
    bl_options = {'REGISTER', 'UNDO'}

    distance_threshold: bpy.props.FloatProperty(name=_('Distance Threshold'), default=0.0, min=0.0)

    @classmethod
    def poll(cls, context):
        if context.mode != 'EDIT_MESH':
            return False

        obj = context.active_object

        if obj is None:
            return False

        return obj.type == 'MESH'

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: bpy.types.Context):
        obj = context.active_object

        distance_threshold = self.distance_threshold

        obj_mesh = obj.data
        shape_keys = obj_mesh.shape_keys
        key_block = shape_keys.key_blocks[obj.active_shape_key_index]
        relative_key_block = key_block.relative_key

        mesh = bmesh.from_edit_mesh(obj_mesh)  # pylint: disable=assignment-from-no-return
        bmesh_vertices = mesh.verts
        for i, (origin, morph) in enumerate(zip(relative_key_block.data, key_block.data)):
            if (origin.co - morph.co).length > distance_threshold:
                bmesh_vertices[i].select_set(True)

        mesh.select_mode |= {'VERT'}
        mesh.select_flush_mode()

        bmesh.update_edit_mesh(obj_mesh)

        return {'FINISHED'}


class RemoveUnusedShapeKeys(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.remove_unused_shape_keys'
    bl_label = _('Remove Unused Shape Keys')
    bl_description = _('Remove unused shape keys from the active meshes')
    bl_options = {'REGISTER', 'UNDO'}

    distance_threshold: bpy.props.FloatProperty(name=_('Distance Threshold'), default=0.0, min=0.0)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        for obj in context.selected_objects:
            if obj.type != 'MESH':
                continue

            used_key_block_names = set()

            distance_threshold = self.distance_threshold

            mesh = obj.data
            shape_keys = mesh.shape_keys
            key_blocks = shape_keys.key_blocks

            for key_block in key_blocks:

                is_used = False

                for origin, morph in zip(mesh.vertices, key_block.data):
                    if (origin.co - morph.co).length > distance_threshold:
                        is_used = True
                        break

                if is_used:
                    used_key_block_names.add(key_block.name)

            # Used shape keys from relative key
            for used_key_block_name in list(used_key_block_names):
                current_key = key_blocks[used_key_block_name]

                while True:
                    relative_key = current_key.relative_key

                    if relative_key.name in used_key_block_names:
                        break

                    used_key_block_names.add(relative_key.name)

                    if current_key.name == relative_key.name:
                        break

                    current_key = relative_key

            for key_block in list(reversed(key_blocks)):
                if key_block.name in used_key_block_names:
                    continue

                # setting the active shapekey
                obj.active_shape_key_index = key_blocks.keys().index(key_block.name)

                # delete it
                bpy.ops.object.shape_key_remove()

        return {'FINISHED'}


class SelectMovedPoseBones(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.select_moved_pose_bones'
    bl_label = _('Select Moved Pose Bones')
    bl_options = {'REGISTER', 'UNDO'}

    select_rotated: bpy.props.BoolProperty(name=_('Rotated'), default=False)
    select_translated: bpy.props.BoolProperty(name=_('Translated'), default=False)
    select_scaled: bpy.props.BoolProperty(name=_('Scaled'), default=False)

    tolerance: bpy.props.FloatProperty(name=_('Tolerance'), default=1e-07)

    def execute(self, context):
        tolerance = self.tolerance

        def isclose(l: float, r: float) -> bool:
            return math.isclose(l, r, abs_tol=tolerance)

        obj: bpy.types.Object
        for obj in context.selected_objects:
            if obj.type != 'ARMATURE':
                continue

            pose_bone: bpy.types.PoseBone
            for pose_bone in obj.pose.bones:
                if not self.select_translated:
                    is_not_translated = True
                else:
                    is_not_translated = isclose(pose_bone.location.x, 0) and isclose(pose_bone.location.y, 0) and isclose(pose_bone.location.z, 0)

                if not self.select_rotated:
                    is_not_rotated = True
                elif pose_bone.rotation_mode == 'QUATERNION':
                    is_not_rotated = isclose(pose_bone.rotation_quaternion.w, 1) and isclose(pose_bone.rotation_quaternion.x, 0) and isclose(pose_bone.rotation_quaternion.y, 0) and isclose(pose_bone.rotation_quaternion.z, 0)
                elif pose_bone.rotation_mode == 'AXIS_ANGLE':
                    is_not_rotated = True
                else:
                    is_not_rotated = isclose(pose_bone.rotation_euler.x, 0) and isclose(pose_bone.rotation_euler.y, 0) and isclose(pose_bone.rotation_euler.z, 0)

                if not self.select_scaled:
                    is_not_scaled = True
                else:
                    is_not_scaled = isclose(pose_bone.scale.x, 1) and isclose(pose_bone.scale.y, 1) and isclose(pose_bone.scale.z, 1)

                if is_not_rotated and is_not_translated and is_not_scaled:
                    continue

                pose_bone.bone.select = True

        return {'FINISHED'}


@dataclasses.dataclass
class Segment:
    index: int
    area: float
    groups: Set[int]
    largest_group: int
    largest_area: float


@dataclasses.dataclass
class Cost:
    weight: float
    angle: float
    material: float
    length: float


@dataclasses.dataclass
class VertexGroupData:
    area: float = 0.0
    adjacent_vertex_group_indices: Set[int] = dataclasses.field(default_factory=set)
    faces: Set[bmesh.types.BMFace] = dataclasses.field(default_factory=set)


LoopPairId = int
VertexPairId = int
VertexGroupPairId = int


def _to_loop_pair_id(loop0: bmesh.types.BMLoop, loop1: bmesh.types.BMLoop, loop_pair_shift: int) -> LoopPairId:
    loop0_index = loop0.index
    loop1_index = loop1.index
    if loop0_index > loop1_index:
        return loop1_index + (loop0_index << loop_pair_shift)
    return loop0_index + (loop1_index << loop_pair_shift)


def _to_vertex_pair_id(vert0: bmesh.types.BMVert, vert1: bmesh.types.BMVert, vertex_pair_shift: int) -> VertexPairId:
    vert0_index = vert0.index
    vert1_index = vert1.index
    if vert0_index > vert1_index:
        return vert1_index + (vert0_index << vertex_pair_shift)
    return vert0_index + (vert1_index << vertex_pair_shift)


def _to_vertex_group_pair_id(vgi0: int, vgi1: int, vertex_group_pair_shift: int) -> VertexGroupPairId:
    if vgi0 > vgi1:
        return vgi1 + (vgi0 << vertex_group_pair_shift)
    return vgi0 + (vgi1 << vertex_group_pair_shift)


def _to_tri_loop_index(loop: bmesh.types.BMLoop) -> int:
    li0 = loop.index
    li1 = loop.link_loop_next.index
    li2 = loop.link_loop_prev.index

    # return min(i0, i1, i2)
    if li0 > li1:
        if li1 > li2:
            return li2
        return li1
    else:
        if li0 > li2:
            return li2
        return li0


class SegmentMeshOperator(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.segment_mesh'
    bl_label = _('Segment Mesh')
    bl_options = {'REGISTER', 'UNDO'}

    maximum_area_threshold: bpy.props.FloatProperty(name=_('Maximum Area Theshold'), default=0.10, min=0, soft_max=1.0)
    minimum_area_threshold: bpy.props.FloatProperty(name=_('Minimum Area Theshold'), default=0.02, min=0, soft_max=1.0)
    weight_threshold: bpy.props.FloatProperty(name=_('Weight Theshold'), default=0.0, min=0, soft_max=1.0)
    segmentation_vertex_color_attribute_name: bpy.props.StringProperty(name=_('Segmentation Vertex Color Attribute Name'), default='controlnet_segmentation')
    segmentation_vertex_color_random_seed: bpy.props.IntProperty(name=_('Segmentation Vertex Color Random Seed'), default=0)

    def execute(self, context: bpy.types.Context):
        maximum_area_threshold = self.maximum_area_threshold
        minimum_area_threshold = self.minimum_area_threshold
        weight_threshold = self.weight_threshold
        segmentation_vertex_color_attribute_name = self.segmentation_vertex_color_attribute_name

        angle_cost_weight = 1.0
        vertex_group_cost_weight = 1.0
        material_cost_weight = 1.0

        mesh_object = context.active_object

        target_bmesh: bmesh.types.BMesh = bmesh.new()

        vertex_groups: bpy.types.VertexGroups = mesh_object.vertex_groups
        ignore_vertex_group_indices = {
            vg.index
            for vg in vertex_groups
            if vg.name in {'mmd_vertex_order', 'mmd_edge_scale'}
        }

        mesh: bpy.types.Mesh = mesh_object.data
        target_bmesh.from_mesh(mesh, face_normals=False, vertex_normals=False)

        deform_layer = target_bmesh.verts.layers.deform.verify()
        vi2vgi2weights: Dict[int, Dict[int, float]] = {
            v.index: {
                vgi: weight
                for vgi, weight in v[deform_layer].items()
                if vgi not in ignore_vertex_group_indices
            }
            for v in target_bmesh.verts
        }

        color_layer = (
            target_bmesh.loops.layers.color[segmentation_vertex_color_attribute_name]
            if segmentation_vertex_color_attribute_name in target_bmesh.loops.layers.color
            else target_bmesh.loops.layers.color.new(segmentation_vertex_color_attribute_name)
        )

        vertex_group_pair_shift = int(math.log2(max(ignore_vertex_group_indices)) + 1)

        try_loops = target_bmesh.calc_loop_triangles()
        loop_count = 3 * len(try_loops)
        loop_pair_shift = int(math.log2(loop_count) / 2 + 1)

        vertex_count = len(target_bmesh.verts)
        vertex_pair_shift = int(math.log2(vertex_count) / 2 + 1)

        vgi2data: Dict[int, VertexGroupData] = collections.defaultdict(lambda: VertexGroupData())

        vpi2weights: Dict[VertexPairId, float] = dict()

        def calc_weight_distance(vert0: bmesh.types.BMVert, vert1: bmesh.types.BMVert) -> float:
            vpi = _to_vertex_pair_id(vert0, vert1, vertex_pair_shift)
            if vpi in vpi2weights:
                return vpi2weights[vpi]

            vgi2weights0 = vi2vgi2weights[vert0.index]
            vgi2weights1 = vi2vgi2weights[vert1.index]

            weight = 0.0
            for vgi0, weight0 in vgi2weights0.items():
                weight += abs(weight0 - vgi2weights1.get(vgi0, 0.0))

            for vgi1, weight1 in vgi2weights1.items():
                weight += abs(weight1 - vgi2weights0.get(vgi1, 0.0))

            return vpi2weights.setdefault(vpi, weight/2)

        # vertex_group_pair_id to cost map
        vgpi2costs: Dict[VertexGroupPairId, Cost] = collections.defaultdict(lambda: Cost(0.0, 0.0, 0.0, 0.0))

        # tri_loop_index to vertex_group_index map
        tli2vgis: Dict[int, int] = dict()

        def to_vertex_group_index(loop: bmesh.types.BMLoop) -> int:
            tli = _to_tri_loop_index(loop)
            if tli in tli2vgis:
                return tli2vgis[tli]

            vgi2weights: Dict[int, float] = dict()
            for loop in (loop.link_loop_prev, loop, loop.link_loop_next):
                loop_edge_length = loop.edge.calc_length()
                for vgi, weight in vi2vgi2weights[loop.vert.index].items():
                    vgi2weights[vgi] = vgi2weights.get(vgi, 0.0) + weight * loop_edge_length

            return tli2vgis.setdefault(
                tli,
                next(
                    iter(sorted(
                        vgi2weights.items(),
                        key=itemgetter(1),
                        reverse=True
                    )),
                    (-1, 0)
                )[0]
            )

        looked_loop_pairs: set[LoopPairId] = set()

        tri_loop: List[bmesh.types.BMLoop, bmesh.types.BMLoop, bmesh.types.BMLoop]
        for tri_loop in try_loops:
            tri_loop0 = tri_loop[0]
            this_vgi = to_vertex_group_index(tri_loop0)
            this_face = tri_loop0.face

            this_data = vgi2data[this_vgi]
            this_data.area += this_face.calc_area()
            this_data.faces.add(this_face)

            for this_loop in tri_loop:
                loop_length = -1
                that_loop = this_loop
                while (that_loop := that_loop.link_loop_radial_next) != this_loop:
                    lpi = _to_loop_pair_id(this_loop, that_loop, loop_pair_shift)
                    if lpi in looked_loop_pairs:
                        continue
                    looked_loop_pairs.add(lpi)

                    that_vgi = to_vertex_group_index(that_loop)
                    if this_vgi == that_vgi:
                        continue

                    vgpi = _to_vertex_group_pair_id(this_vgi, that_vgi, vertex_group_pair_shift)

                    if loop_length < 0:
                        this_edge = this_loop.edge
                        loop_length = this_edge.calc_length()
                        this_verts = this_edge.verts
                        vert0 = this_verts[0]
                        vert1 = this_verts[1]
                        this_vert2 = this_loop.link_loop_prev.vert

                        this_loop_weight_distance = calc_weight_distance(vert0, this_vert2) + calc_weight_distance(vert1, this_vert2)

                    cost = vgpi2costs[vgpi]
                    cost.length += loop_length

                    that_vert2 = that_loop.link_loop_prev.vert
                    cost.weight += loop_length * (this_loop_weight_distance + calc_weight_distance(vert0, that_vert2) + calc_weight_distance(vert1, that_vert2))

                    cost.angle += loop_length * (this_loop.calc_normal().angle(that_loop.calc_normal()))

                    that_face = that_loop.face
                    cost.material += loop_length * (0 if this_face.material_index == that_face.material_index else 1)

                    this_data.adjacent_vertex_group_indices.add(that_vgi)
                    vgi2data[that_vgi].adjacent_vertex_group_indices.add(this_vgi)

        vgi2segment: Dict[int, Segment] = {
            vgi: Segment(si, data.area, {vgi}, vgi, data.area)
            for si, (vgi, data) in enumerate(vgi2data.items())
        }

        # with open('output.tsv', 'wt') as f:
        #     for vgi, data in vgi2data.items():
        #         for v in data.adjacent_vertex_group_indices:
        #             cost = vgpi2costs[_to_vertex_group_pair_id(vgi, v, vertex_group_pair_shift)]
        #             print(f'{vertex_groups[vgi].name}\t{vertex_groups[v].name}\t{cost.length}\t{cost.angle}\t{cost.material}\t{cost.weight}', file=f)

        # angle/length threshold 0.3

        def merge(src: Segment, dst: Segment):
            if dst.largest_area < src.largest_area:
                dst.largest_group = src.largest_group
                dst.largest_area = src.largest_area
            dst.area += src.area
            dst.groups.update(src.groups)
            replace_index = src.index
            for vgi, segment in vgi2segment.items():
                if segment.index != replace_index:
                    continue
                vgi2segment[vgi] = dst

        for vgpi, cost in vgpi2costs.items():
            pass

        data: VertexGroupData
        for vgi, data in sorted(vgi2data.items(), key=lambda e: e[1].area):
            segment = vgi2segment[vgi]
            if maximum_area_threshold <= segment.area:
                continue

            merging = True
            while merging:
                merging = False

                for adjacent_segment in sorted((vgi2segment[avgi] for avgi in data.adjacent_vertex_group_indices), key=lambda e: e.area):
                    if segment.index == adjacent_segment.index:
                        continue

                    merged_area = segment.area + adjacent_segment.area
                    if maximum_area_threshold <= merged_area and minimum_area_threshold < segment.area:
                        continue

                    merge(adjacent_segment, segment)
                    merging = True
                    break

        segments = [next(s) for i, (_, s) in enumerate(itertools.groupby(sorted(vgi2segment.values(), key=lambda e: e.index), key=lambda e: e.index))]

        if len(segments) > len(SEGMANTATION_COLORS):
            self.report(type={'ERROR'}, message='Too many segments; increase the Maximum Area Theshold to reduce the segments.')
            return {'CANCELLED'}

        # data_materials = bpy.data.materials
        # setup_controlnet_segment_materials(data_materials)

        segmantation_colors = SEGMANTATION_COLORS.copy()
        rng = random.Random(self.segmentation_vertex_color_random_seed)
        rng.shuffle(segmantation_colors)

        for index, segment in enumerate(segments):
            # material_name = f'controlnet_segment.{index:03}'
            # if index + 1 < len(mesh_materials):
            #     mesh_materials[index] = data_materials[material_name]
            # else:
            #     mesh_materials.append(data_materials[material_name])

            segmentation_color = segmantation_colors[index]

            for face in (f for vgi in segment.groups for f in vgi2data[vgi].faces):
                # face.material_index = index
                for this_loop in face.loops:
                    this_loop[color_layer] = segmentation_color

        target_bmesh.to_mesh(mesh)

        for material in mesh.materials:
            setup_output_aov(material.node_tree, segmentation_vertex_color_attribute_name)

        if not segmentation_vertex_color_attribute_name in context.view_layer.aovs:
            aov = context.view_layer.aovs.add()
            aov.name = segmentation_vertex_color_attribute_name

        # for segment in sorted(segments, key=lambda s: s.area):
        #     print(segment, [vertex_groups[vgi].name for vgi in segment.groups])

        return {'FINISHED'}


RGBA = Tuple[float, float, float, float]


def setup_controlnet_segment_materials(data_materials: bpy.types.BlendDataMaterials):
    for index, rgba in enumerate(SEGMANTATION_COLORS):
        name = f'controlnet_segment.{index:03}'
        if name in data_materials:
            continue

        material = data_materials.new(name=name)
        material.use_nodes = True
        material.use_fake_user = True
        setup_shader(material.node_tree, rgba)


def setup_output_aov(node_tree: bpy.types.NodeTree, segmentation_output_aov_name: str):
    nodes = node_tree.nodes
    segmentation_output_aov_node: Optional[bpy.types.ShaderNodeOutputAOV] = next((n for n in nodes if n.type == 'OUTPUT_AOV' and n.name == segmentation_output_aov_name), None)
    if segmentation_output_aov_node is None:
        segmentation_output_aov_node = nodes.new(type=bpy.types.ShaderNodeOutputAOV.__name__)
        segmentation_output_aov_node.name = segmentation_output_aov_name
        segmentation_output_aov_node.location = (300, 600)

    if len(segmentation_output_aov_node.inputs['Color'].links) > 0:
        return

    segmentation_vertex_color_node: bpy.types.ShaderNodeVertexColor = nodes.new(type=bpy.types.ShaderNodeVertexColor.__name__)
    segmentation_vertex_color_node.layer_name = segmentation_output_aov_name
    segmentation_vertex_color_node.location = (0, 600)
    node_tree.links.new(
        segmentation_vertex_color_node.outputs[0],
        segmentation_output_aov_node.inputs[0]
    )


def setup_shader(node_tree: bpy.types.NodeTree, rgba: RGBA):
    if node_tree:
        node_tree.links.clear()
        node_tree.nodes.clear()
    nodes = node_tree.nodes
    links = node_tree.links
    output = nodes.new(type=bpy.types.ShaderNodeOutputMaterial.__name__)
    output.location = (300, 0)
    emission = nodes.new(type=bpy.types.ShaderNodeEmission.__name__)
    emission.location = (0, 0)
    emission.inputs[0].default_value = rgba
    emission.inputs[1].default_value = 1

    links.new(emission.outputs[0], output.inputs[0])


def to_blender_color(c):
    c = min(max(0, c), 255) / 255
    return c / 12.92 if c < 0.04045 else math.pow((c + 0.055) / 1.055, 2.4)


SEGMANTATION_COLORS: List[RGBA] = [
    (
        to_blender_color(0xff & (rgb >> 16)),  # Red
        to_blender_color(0xff & (rgb >> 8)),  # Blue
        to_blender_color(0xff & (rgb)),  # Green
        1.0,  # Alpha
    )
    for rgb in [
        0xff0000, 0xffa300, 0xff6600, 0xc2ff00, 0x008fff, 0x33ff00, 0x0052ff, 0x00ff29,
        0x00ffad, 0x0a00ff, 0xadff00, 0x00ff99, 0xff5c00, 0xff00ff, 0xff00f5, 0xff0066,
        0xffad00, 0xff0014, 0xffb8b8, 0x001fff, 0x00ff3d, 0x0047ff, 0xff00cc, 0x00ffc2,
        0x00ff52, 0x000aff, 0x0070ff, 0x3300ff, 0x00c2ff, 0x007aff, 0x00ffa3, 0xff9900,
        0x00ff0a, 0xff7000, 0x8fff00, 0x5200ff, 0xa3ff00, 0xffeb00, 0x08b8aa, 0x8500ff,
        0x00ff5c, 0xb800ff, 0xff001f, 0x00b8ff, 0x00d6ff, 0xff0070, 0x5cff00, 0x00e0ff,
        0x70e0ff, 0x46b8a0, 0xa300ff, 0x9900ff, 0x47ff00, 0xff00a3, 0xffcc00, 0xff008f,
        0x00ffeb, 0x85ff00, 0xff00eb, 0xf500ff, 0xff007a, 0xfff500, 0x0abed4, 0xd6ff00,
        0x00ccff, 0x1400ff, 0xffff00, 0x0099ff, 0x0029ff, 0x00ffcc, 0x2900ff, 0x29ff00,
        0xad00ff, 0x00f5ff, 0x4700ff, 0x7a00ff, 0x00ffb8, 0x005cff, 0xb8ff00, 0x0085ff,
        0xffd600, 0x19c2c2, 0x66ff00, 0x5c00ff,
    ]
]

# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from dataclasses import dataclass
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


@dataclass
class Segment:
    index: int
    area: float
    groups: Set[int]
    largest_group: int
    largest_area: float


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
        mesh_object = context.active_object

        target_bmesh: bmesh.types.BMesh = bmesh.new()

        vertex_groups: bpy.types.VertexGroups = mesh_object.vertex_groups
        ignore_vertex_group_indices = {
            vg.index
            for vg in vertex_groups
            if vg.name in {'mmd_vertex_order', 'mmd_edge_scale'}
        }

        mesh: bpy.types.Mesh = mesh_object.data
        target_bmesh.from_mesh(mesh, face_normals=False)
        deform_layer = target_bmesh.verts.layers.deform.verify()
        color_layer = (
            target_bmesh.loops.layers.color[segmentation_vertex_color_attribute_name]
            if segmentation_vertex_color_attribute_name in target_bmesh.loops.layers.color
            else target_bmesh.loops.layers.color.new(segmentation_vertex_color_attribute_name)
        )

        vgi2adjacent_vgis: Dict[int, Set[int]] = dict()

        vgi2area: Dict[int, float] = dict()

        vgi2fis: Dict[int, Set[int]] = dict()

        vgi2weight: Dict[int, float] = dict()

        face: bmesh.types.BMFace
        for face in target_bmesh.faces:
            vgi2weight.clear()
            vert: bmesh.types.BMVert
            for vert in face.verts:
                for vertex_group_index, weight in vert[deform_layer].items():
                    if weight < weight_threshold:
                        continue
                    if vertex_group_index in ignore_vertex_group_indices:
                        continue
                    vgi2weight[vertex_group_index] = vgi2weight.get(vertex_group_index, 0.0) + weight

            sorted_vgi2weight = sorted(vgi2weight.items(), key=itemgetter(1), reverse=True)
            # for f in sorted_vgi2weight:
            #     for t in sorted_vgi2weight:
            #         if f == t:
            #             continue
            #         vgi2adjacent_vgis.setdefault(f[0], set()).add(t[0])

            if len(sorted_vgi2weight) > 1:
                f = sorted_vgi2weight[0][0]
                t = sorted_vgi2weight[1][0]
                vgi2adjacent_vgis.setdefault(f, set()).add(t)
                vgi2adjacent_vgis.setdefault(t, set()).add(f)

            vertex_group_index = sorted_vgi2weight[0][0]
            vgi2area[vertex_group_index] = vgi2area.get(vertex_group_index, 0.0) + face.calc_area()
            vgi2fis.setdefault(vertex_group_index, set()).add(face.index)

        vgi2segment: Dict[int, Segment] = {
            gi: Segment(si, area, {gi}, gi, area)
            for si, (gi, area) in enumerate(vgi2area.items())
        }

        for vgi, avgis in vgi2adjacent_vgis.items():
            print(vgi, avgis)

        def merge(src: Segment, dst: Segment):
            if dst.largest_area < src.largest_area:
                dst.largest_group = src.largest_group
                dst.largest_area = src.largest_area
            dst.area += src.area
            dst.groups.update(src.groups)
            replace_index = src.index
            for gi, segment in vgi2segment.items():
                if segment.index != replace_index:
                    continue
                vgi2segment[gi] = dst

        for vgi, _ in sorted(vgi2area.items(), key=itemgetter(1)):
            if vgi not in vgi2adjacent_vgis:
                continue

            if vgi not in vgi2segment:
                continue

            segment = vgi2segment[vgi]
            if maximum_area_threshold <= segment.area:
                continue

            merging = True
            while merging:
                merging = False

                for adjacent_segment in sorted((vgi2segment[avgi] for avgi in vgi2adjacent_vgis[vgi] if avgi in vgi2segment), key=lambda e: e.area):
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

        faces = target_bmesh.faces
        faces.ensure_lookup_table()

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

            for fid in (fi for gi in segment.groups for fi in vgi2fis[gi]):
                face = faces[fid]
                # face.material_index = index
                for loop in face.loops:
                    loop[color_layer] = segmentation_color

        target_bmesh.to_mesh(mesh)

        for material in mesh.materials:
            setup_output_aov(material.node_tree, segmentation_vertex_color_attribute_name)

        if not segmentation_vertex_color_attribute_name in context.view_layer.aovs:
            aov = context.view_layer.aovs.add()
            aov.name = segmentation_vertex_color_attribute_name

        for segment in sorted(segments, key=lambda s: s.area):
            print(segment, [vertex_groups[vgi].name for vgi in segment.groups])

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

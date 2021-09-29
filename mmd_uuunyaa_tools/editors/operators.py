# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import math
from typing import Set

import bmesh
import bpy
from mathutils import Quaternion, Vector
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
        eevee.ssr_border_fade = 0.000

        # Motion Blur
        eevee.use_motion_blur = self.use_motion_blur

        # Shadows
        # > Cube Size 1024 px
        eevee.shadow_cube_size = '1024'
        # > Cascade Size 2048 px
        eevee.shadow_cascade_size = '2048'

        # Indirect lighting: enable
        # > Irradiance Smoothing: 0.50
        eevee.gi_irradiance_smoothing = 0.50

        # Film > Transparent
        bpy.data.scenes['Scene'].render.film_transparent = self.film_transparent

        # Color Management > Look: High Contrast
        bpy.data.scenes['Scene'].view_settings.look = 'High Contrast'

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

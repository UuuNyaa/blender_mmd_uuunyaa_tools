# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import re
from typing import Set

import bmesh
import bpy

from mmd_uuunyaa_tools.utilities import (import_mmd_tools,
                                         is_mmd_tools_installed,
                                         label_multiline)


class ConvertMaterialsForEevee(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.convert_materials_for_eevee'
    bl_label = 'Convert Shaders for Eevee'
    bl_description = 'Convert materials of selected objects for Eevee.'
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
    bl_label = 'Setup Render Engine for Eevee'
    bl_description = 'Setup render engine properties for Eevee.'
    bl_options = {'REGISTER', 'UNDO'}

    use_bloom: bpy.props.BoolProperty(name='Use Bloom', default=True)
    use_motion_blur: bpy.props.BoolProperty(name='Use Motion Blur', default=False)
    film_transparent: bpy.props.BoolProperty(name='Use Film Transparent', default=False)

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
    bl_label = 'Show Message Box'
    bl_description = 'Show message box.'
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


class SelectRelatedObjects(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.select_related_objects'
    bl_label = 'Select Related Objects'
    bl_description = 'Select related objects.'
    bl_options = {'REGISTER', 'UNDO'}

    type_to_name_func = {
        'RIGID_BODY': lambda o: o.mmd_rigid.name_j,
        'JOINT': lambda o: o.mmd_joint.name_j,
    }

    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj.mmd_type in {'RIGID_BODY', 'JOINT'}:
                return True
        return False

    def execute(self, context):
        mmd_model = import_mmd_tools().core.model.Model

        origin_objects = set(context.selected_objects)
        while origin_objects:
            origin_object = origin_objects.pop()
            origin_type = origin_object.mmd_type
            if origin_type == 'NONE':
                continue

            to_name = self.type_to_name_func[origin_type]

            match = re.match(r'(.+)[_＿\-]([0-9]+)[_＿\-]([0-9]+)', to_name(origin_object))
            if match is None:
                continue

            pattern = match.group(1) + r'[_＿\-]([0-9]+)[_＿\-]([0-9]+)'

            root = mmd_model.findRoot(origin_object)

            for obj in context.view_layer.objects:
                if obj.mmd_type != origin_type:
                    continue

                if mmd_model.findRoot(obj) != root:
                    continue

                if re.match(pattern, to_name(obj)) is None:
                    continue

                if obj in origin_objects:
                    origin_objects.remove(obj)
                else:
                    obj.select_set(True)

        return {'FINISHED'}


class SelectRelatedBones(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.select_related_bones'
    bl_label = 'Select Related Bones'
    bl_description = 'Select related bones.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_ARMATURE'

    def execute(self, context):
        origin_editable_bones = set(context.selected_editable_bones)

        while origin_editable_bones:
            origin_editable_bone = origin_editable_bones.pop()
            armature = origin_editable_bone.id_data

            match = re.match(r'(.+)[_＿\-]([0-9]+)[_＿\-]([0-9]+)', origin_editable_bone.name)
            if match is None:
                continue

            pattern = match.group(1) + r'[_＿\-]([0-9]+)[_＿\-]([0-9]+)'

            for bone in armature.edit_bones:
                if re.match(pattern, bone.name) is None:
                    continue

                if bone in origin_editable_bones:
                    origin_editable_bones.remove(bone)
                else:
                    bone.select = True

        return {'FINISHED'}


class SelectRelatedPoseBones(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.select_related_pose_bones'
    bl_label = 'Select Related Pose Bones'
    bl_description = 'Select related pose bones.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        origin_pose_bones = set(context.selected_pose_bones)

        while origin_pose_bones:
            origin_pose_bone = origin_pose_bones.pop()
            armature = origin_pose_bone.id_data

            match = re.match(r'(.+)[_＿\-]([0-9]+)[_＿\-]([0-9]+)', origin_pose_bone.name)
            if match is None:
                continue

            pattern = match.group(1) + r'[_＿\-]([0-9]+)[_＿\-]([0-9]+)'

            for pose_bone in armature.pose.bones:
                if re.match(pattern, pose_bone.name) is None:
                    continue

                if pose_bone in origin_pose_bones:
                    origin_pose_bones.remove(pose_bone)
                else:
                    pose_bone.bone.select = True

        return {'FINISHED'}


class RemoveUnusedVertexGroups(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.remove_unused_vertex_groups'
    bl_label = 'Remove Unused Vertex Groups'
    bl_description = 'Remove unused vertex groups from the active meshes'
    bl_options = {'REGISTER', 'UNDO'}

    weight_threshold: bpy.props.FloatProperty(name='Weight Threshold', default=0.0, min=0.0, max=1.0)

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
    bl_label = 'Select Shape Key Target Vertices'
    bl_description = 'Select shape key target vertices from the active meshes'
    bl_options = {'REGISTER', 'UNDO'}

    distance_threshold: bpy.props.FloatProperty(name='Distance Threshold', default=0.0, min=0.0)

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
    bl_label = 'Remove Unused Shape Keys'
    bl_description = 'Remove unused shape keys from the active meshes'
    bl_options = {'REGISTER', 'UNDO'}

    distance_threshold: bpy.props.FloatProperty(name='Distance Threshold', default=0.0, min=0.0)

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

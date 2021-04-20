# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from typing import Iterable, Union

import bpy
from mmd_uuunyaa_tools.editors.armatures import MetarigArmatureObject, MMDArmatureObject, MMDRigifyArmatureObject, RigifyArmatureObject
from mmd_uuunyaa_tools.utilities import MessageException, import_mmd_tools


class MMDArmatureAddMetarig(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_armature_add_metarig'
    bl_label = 'Add Human (metarig) from MMD Armature'
    bl_description = 'Add human (metarig) from MMD armature.'
    bl_options = {'REGISTER', 'UNDO'}

    is_clean_armature: bpy.props.BoolProperty(name='Clean Armature', default=True)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return False

        if len(context.selected_objects) != 1:
            return False

        return MMDArmatureObject.is_mmd_armature_object(context.active_object)

    def create_metarig_object(self) -> bpy.types.Object:
        original_cursor_location = bpy.context.scene.cursor.location
        try:
            # Rigifyのメタリグはどこに置いたとしても、
            # 生成ボタンをおすと(0, 0, 0)にRigifyArmatureが生成される。
            # よってメタリグも(0, 0, 0)に生成するようにする。
            bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
            bpy.ops.object.armature_human_metarig_add()
            return bpy.context.object
        except AttributeError as e:
            if str(e) != 'Calling operator "bpy.ops.object.armature_human_metarig_add" error, could not be found':
                raise
            raise MessageException('Failed to invoke Rigify\nPlease enable Rigify add-on.')
        finally:
            bpy.context.scene.cursor.location = original_cursor_location

    def execute(self, context: bpy.types.Context):
        mmd_object = context.active_object

        try:
            metarig_object = MetarigArmatureObject(self.create_metarig_object())
        except MessageException as e:
            self.report(type={'ERROR'}, message=str(e))
            return {'CANCELLED'}

        mmd_armature_object = MMDArmatureObject(mmd_object)
        metarig_object.fit_scale(mmd_armature_object)

        mmd_object.select = True
        metarig_object.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        if self.is_clean_armature:
            mmd_armature_object.clean_armature_fingers()
            mmd_armature_object.clean_armature_spine()

        metarig_object.fit_bones(mmd_armature_object)

        bpy.ops.object.mode_set(mode='POSE')
        metarig_object.set_rigify_parameters()

        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


class MMDRigifyIntegrate(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.mmd_rigify_integrate'
    bl_label = 'Integrate Rigify and MMD Armatures'
    bl_description = 'Integrate Rigify and MMD armatures.'
    bl_options = {'REGISTER', 'UNDO'}

    is_join_armatures: bpy.props.BoolProperty(name='Join Aarmtures', description='Join MMD and Rigify armatures', default=True)
    mmd_main_bone_layer: bpy.props.IntProperty(name='MMD main bone layer', default=24, min=0, max=31)
    mmd_others_bone_layer: bpy.props.IntProperty(name='MMD others bone layer', default=25, min=0, max=31)
    mmd_shadow_bone_layer: bpy.props.IntProperty(name='MMD shadow bone layer', default=26, min=0, max=31)
    mmd_dummy_bone_layer: bpy.props.IntProperty(name='MMD dummy bone layer', default=27, min=0, max=31)

    @classmethod
    def find_armature_objects(cls, objects: Iterable[bpy.types.Object]) -> (Union[bpy.types.Object, None], Union[bpy.types.Object, None]):
        mmd_tools = import_mmd_tools()

        rigify_object: Union[bpy.types.Object, None] = None
        mmd_object: Union[bpy.types.Object, None] = None

        for obj in objects:
            if obj.type != 'ARMATURE':
                continue

            if 'rig_id' in obj.data:
                rigify_object = obj
                continue

            mmd_root = mmd_tools.core.model.Model.findRoot(obj)
            if mmd_root is not None:
                mmd_object = obj
                continue

        return (rigify_object, mmd_object)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        if context.mode != 'OBJECT':
            return False

        selected_objects = bpy.context.selected_objects
        if len(selected_objects) != 2:
            return False

        rigify_object, mmd_object = cls.find_armature_objects(selected_objects)

        return mmd_object is not None and rigify_object is not None

    def change_mmd_bone_layer(self, mmd_armature_object: MMDArmatureObject):
        mmd_bones = mmd_armature_object.bones
        for mmd_rigify_bone in mmd_armature_object.mmd_rigify_bones:
            mmd_bones[mmd_rigify_bone.mmd_bone_name].layers[23] = True

    def set_view_layers(self, rigify_armature_object: bpy.types.Object):
        rig_armature: bpy.types.Armature = rigify_armature_object.raw_armature
        rig_armature.layers = [i in {0, 3, 5, 7, 10, 13, 16, 28} for i in range(32)]

    def join_armatures(self, rigify_armature_object: RigifyArmatureObject, mmd_armature_object: MMDArmatureObject):
        mmd_main_bone_layer = self.mmd_main_bone_layer
        mmd_others_bone_layer = self.mmd_others_bone_layer
        mmd_shadow_bone_layer = self.mmd_shadow_bone_layer
        mmd_dummy_bone_layer = self.mmd_dummy_bone_layer

        mmd_armature = mmd_armature_object.raw_armature
        mmd_armature.layers = [i in {0, 8, 9, 23, mmd_main_bone_layer, mmd_others_bone_layer, mmd_shadow_bone_layer, mmd_dummy_bone_layer} for i in range(32)]

        mmd_bind_bones = {b.name for b in mmd_armature_object.bones.values()}

        for bone in mmd_armature.bones.values():
            if bone.layers[0] == True:
                bone.layers = [i in {mmd_main_bone_layer} for i in range(32)]
                if bone.name not in mmd_bind_bones:
                    bone.layers[mmd_others_bone_layer] = True

            elif bone.layers[8] == True:
                bone.layers = [i in {mmd_shadow_bone_layer} for i in range(32)]

            elif bone.layers[9] == True:
                bone.layers = [i in {mmd_dummy_bone_layer} for i in range(32)]

            elif bone.layers[23] == True:
                bone.layers[23] = False

        rigify_armature: bpy.types.Armature = rigify_armature_object.raw_armature
        layers = rigify_armature.layers
        rig_id = rigify_armature['rig_id']

        bpy.context.view_layer.objects.active = mmd_armature_object.raw_object
        bpy.ops.object.join()
        mmd_armature.layers = layers
        mmd_armature['rig_id'] = rig_id
        mmd_armature_object.raw_object.draw_type = 'WIRE'

        mmd_armature.layers[mmd_main_bone_layer] = False
        mmd_armature.layers[mmd_others_bone_layer] = True
        mmd_armature.layers[mmd_shadow_bone_layer] = False
        mmd_armature.layers[mmd_dummy_bone_layer] = False

        mmd_armature_object.raw_object.show_x_ray = True

    def execute(self, context: bpy.types.Context):
        rigify_armature_object, mmd_armature_object = self.find_armature_objects(context.selected_objects)

        rigify_armature_object = MMDRigifyArmatureObject(rigify_armature_object)
        mmd_armature_object = MMDArmatureObject(mmd_armature_object)

        self.change_mmd_bone_layer(mmd_armature_object)

        bpy.ops.object.mode_set(mode='EDIT')
        rigify_armature_object.remove_unused_face_bones()
        rigify_armature_object.fit_bone_rotations(mmd_armature_object)
        rigify_armature_object.imitate_mmd_bone_behavior(mmd_armature_object)

        bpy.ops.object.mode_set(mode='POSE')
        rigify_armature_object.imitate_mmd_pose_behavior()
        rigify_armature_object.pose_bone_constraints()
        rigify_armature_object.bind_bones(mmd_armature_object)

        bpy.ops.object.mode_set(mode='OBJECT')
        rigify_armature_object.assign_mmd_bone_names()
        self.set_view_layers(rigify_armature_object)

        if self.is_join_armatures:
            self.join_armatures(rigify_armature_object, mmd_armature_object)

        return {'FINISHED'}


class MMDRigifyConvert(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.rigify_to_mmd_compatible'
    bl_label = 'Convert Rigify Armature to MMD compatible'
    bl_description = 'Convert Rigify armature to MMD compatible.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False

        active_object = context.active_object

        return RigifyArmatureObject.is_rigify_armature_object(active_object) and not MMDRigifyArmatureObject.is_mmd_integrated_object(active_object)

    def execute(self, context: bpy.types.Context):
        rigify_armature_object = RigifyArmatureObject(context.active_object)

        bpy.ops.object.mode_set(mode='EDIT')
        rigify_armature_object.imitate_mmd_bone_behavior()

        bpy.ops.object.mode_set(mode='POSE')
        rigify_armature_object.pose_bone_constraints()
        rigify_armature_object.imitate_mmd_pose_behavior()
        rigify_armature_object.set_bone_groups()

        bpy.ops.object.mode_set(mode='OBJECT')
        rigify_armature_object.assign_mmd_bone_names()
        return {'FINISHED'}


class MMDRigifyApplyMMDRestPose(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.rigify_apply_mmd_rest_pose'
    bl_label = 'Apply MMD Rest Pose'
    bl_description = 'Apply MMD rest pose.'
    bl_options = {'REGISTER', 'UNDO'}

    iterations: bpy.props.IntProperty(name='Iterations', description='Number of solving iterations', default=7, min=1, max=100)
    pose_arms: bpy.props.BoolProperty(name='Pose arms', default=True)
    pose_legs: bpy.props.BoolProperty(name='Pose legs', default=True)
    pose_fingers: bpy.props.BoolProperty(name='Pose fingers', default=False)

    @classmethod
    def poll(cls, context):
        if context.mode not in {'OBJECT', 'POSE'}:
            return False

        active_object = context.active_object

        return RigifyArmatureObject.is_rigify_armature_object(active_object)

    def execute(self, context: bpy.types.Context):
        previous_mode = context.mode

        try:
            rigify_armature_object = RigifyArmatureObject(context.active_object)
            dependency_graph = context.evaluated_depsgraph_get()

            bpy.ops.object.mode_set(mode='POSE')
            rigify_armature_object.pose_mmd_rest(
                dependency_graph,
                self.iterations,
                pose_arms=self.pose_arms,
                pose_legs=self.pose_legs,
                pose_fingers=self.pose_fingers
            )

        finally:
            bpy.ops.object.mode_set(mode=previous_mode)

        return {'FINISHED'}

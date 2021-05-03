# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
from mmd_uuunyaa_tools.editors.armatures import ControlType
from mmd_uuunyaa_tools.editors.armatures.rigify import MMDRigifyArmatureObject


class OperatorPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_mmd_rigify'
    bl_label = 'UuuNyaa MMD Rigify'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_context = ''

    @classmethod
    def poll(cls, context):
        active_object = context.active_object
        if not active_object:
            return False

        if active_object.type != 'ARMATURE':
            return False

        if active_object.data.get('rig_id') is None:
            return False

        prop_storage_bone = context.active_object.pose.bones.get(MMDRigifyArmatureObject.prop_storage_bone_name)
        if prop_storage_bone is None:
            return False

        if MMDRigifyArmatureObject.prop_name_mmd_rigify_bind_mmd_rigify not in prop_storage_bone:
            return False

        return True

    def draw(self, context: bpy.types.Context):
        # pylint: disable=too-many-locals
        active_object = context.active_object
        pose_bones = context.active_object.pose.bones

        rigify_armature_object = MMDRigifyArmatureObject(active_object)
        bind_mmd_rigify = rigify_armature_object.datapaths[ControlType.BIND_MMD_RIGIFY]
        eye_mmd_rigify = rigify_armature_object.datapaths[ControlType.EYE_MMD_RIGIFY]
        toe_l_mmd_rigify = rigify_armature_object.datapaths[ControlType.TOE_L_MMD_RIGIFY]
        toe_r_mmd_rigify = rigify_armature_object.datapaths[ControlType.TOE_R_MMD_RIGIFY]
        arm_l_ik_fk = rigify_armature_object.datapaths[ControlType.ARM_L_IK_FK]
        arm_r_ik_fk = rigify_armature_object.datapaths[ControlType.ARM_R_IK_FK]
        leg_l_ik_fk = rigify_armature_object.datapaths[ControlType.LEG_L_IK_FK]
        leg_r_ik_fk = rigify_armature_object.datapaths[ControlType.LEG_R_IK_FK]

        layout = self.layout
        col = layout.column()

        col.label(text='MMD-Rigify:')
        col.prop(pose_bones[bind_mmd_rigify.bone_name], bind_mmd_rigify.prop_data_path, text='Bind', slider=True)
        col.prop(pose_bones[eye_mmd_rigify.bone_name], eye_mmd_rigify.prop_data_path, text='Eyes', slider=True)
        row = col.row()
        row.prop(pose_bones[toe_l_mmd_rigify.bone_name], toe_l_mmd_rigify.prop_data_path, text='Toe.L', slider=True)
        row.prop(pose_bones[toe_r_mmd_rigify.bone_name], toe_r_mmd_rigify.prop_data_path, text='Toe.R', slider=True)

        col.label(text='IK-FK:')
        row = col.row()
        row.prop(pose_bones[arm_l_ik_fk.bone_name], arm_l_ik_fk.prop_data_path, text='Arm.L', slider=True)
        row.prop(pose_bones[arm_r_ik_fk.bone_name], arm_r_ik_fk.prop_data_path, text='Arm.R', slider=True)
        row = col.row()
        row.prop(pose_bones[leg_l_ik_fk.bone_name], leg_l_ik_fk.prop_data_path, text='Leg.L', slider=True)
        row.prop(pose_bones[leg_r_ik_fk.bone_name], leg_r_ik_fk.prop_data_path, text='Leg.R', slider=True)

        if not MMDRigifyArmatureObject.is_mmd_integrated_object(active_object):
            return

        col.label(text='MMD Layers:')
        row = col.row()
        row.prop(context.active_object.data, 'layers', index=24, toggle=True, text='Main')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=25, toggle=True, text='Others')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=26, toggle=True, text='Shadow')

        row = col.row()
        row.prop(context.active_object.data, 'layers', index=27, toggle=True, text='Dummy')

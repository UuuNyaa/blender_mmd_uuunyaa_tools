# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
from mmd_uuunyaa_tools.editors.armatures import ControlType, GroupType, group_type2prop_names, MMDRigifyArmatureObject


class OperatorPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_mmd_rigify'
    bl_label = 'UuuNyaa MMD Rigify'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_context = ''

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False

        return context.object.type == 'ARMATURE' and context.active_object.data.get('rig_id') is not None

    def draw(self, context: bpy.types.Context):
        active_object = bpy.context.active_object
        pose_bones = bpy.context.active_object.pose.bones

        if group_type2prop_names[GroupType.TORSO] not in pose_bones['torso']:
            return

        rigify_armature_object = MMDRigifyArmatureObject(active_object)
        arm_l_ik_fk = rigify_armature_object.datapaths[ControlType.ARM_L_IK_FK]
        arm_r_ik_fk = rigify_armature_object.datapaths[ControlType.ARM_R_IK_FK]
        leg_l_ik_fk = rigify_armature_object.datapaths[ControlType.LEG_L_IK_FK]
        leg_r_ik_fk = rigify_armature_object.datapaths[ControlType.LEG_R_IK_FK]

        layout = self.layout
        col = layout.column()

        col.label(text='MMD-Rigify:')
        row = col.row()
        row.prop(pose_bones['torso'], '["mmd_rigify_eye_mmd_rigify"]', text='Eyes', slider=True)

        col.label(text='IK-FK:')
        row = col.row()
        row.prop(pose_bones[arm_l_ik_fk.bone_name], f'["{arm_l_ik_fk.prop_name}"]', text='Arm.L', slider=True)
        row.prop(pose_bones[arm_r_ik_fk.bone_name], f'["{arm_r_ik_fk.prop_name}"]', text='Arm.R', slider=True)
        row = col.row()
        row.prop(pose_bones[leg_l_ik_fk.bone_name], f'["{leg_l_ik_fk.prop_name}"]', text='Leg.L', slider=True)
        row.prop(pose_bones[leg_r_ik_fk.bone_name], f'["{leg_r_ik_fk.prop_name}"]', text='Leg.R', slider=True)

        if not MMDRigifyArmatureObject.is_mmd_integrated_object(active_object):
            return

        col.label(text='Influences:')
        row = col.row()
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.FACE]}"]', text='Face', slider=True)
        row = col.row()
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.TORSO]}"]', text='Torso', slider=True)
        row = col.row()
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.ARM_L]}"]', text='Arm.L', slider=True)
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.ARM_R]}"]', text='Arm.R', slider=True)
        row = col.row()
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.LEG_L]}"]', text='Leg.L', slider=True)
        row.prop(pose_bones['torso'], f'["{group_type2prop_names[GroupType.LEG_R]}"]', text='Leg.R', slider=True)

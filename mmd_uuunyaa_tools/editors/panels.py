# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
from mmd_uuunyaa_tools.editors.armatures import GroupType, group_type2prop_names


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
        pose_bones = bpy.context.active_object.pose.bones

        if group_type2prop_names[GroupType.TORSO] not in pose_bones['torso']:
            return

        layout = self.layout
        col = layout.column()

        col.label(text='MMD-Rigify:')
        row = col.row()
        row.prop(pose_bones['torso'], '["mmd_rigify_eye_mmd_rigify"]', text='Eyes', slider=True)

        col.label(text='IK-FK:')
        row = col.row()
        row.prop(pose_bones['upper_arm_parent.L'], '["IK_FK"]', text='Arm.L', slider=True)
        row.prop(pose_bones['upper_arm_parent.R'], '["IK_FK"]', text='Arm.R', slider=True)
        row = col.row()
        row.prop(pose_bones['thigh_parent.L'], '["IK_FK"]', text='Leg.L', slider=True)
        row.prop(pose_bones['thigh_parent.R'], '["IK_FK"]', text='Leg.R', slider=True)

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

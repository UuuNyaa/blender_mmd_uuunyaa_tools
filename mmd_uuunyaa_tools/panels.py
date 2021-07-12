# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy

from mmd_uuunyaa_tools.converters.armatures.operators import (
    MMDArmatureAddMetarig, MMDAutoRigApplyMMDRestPose, MMDAutoRigConvert,
    MMDRigifyApplyMMDRestPose, MMDRigifyBind, MMDRigifyConvert,
    MMDRigifyIntegrate)
from mmd_uuunyaa_tools.editors.operators import (ConvertMaterialsForEevee,
                                                 SetupRenderEngineForEevee)
from mmd_uuunyaa_tools.m17n import _


class OperatorPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_operator_panel'
    bl_label = 'UuuNyaa Operator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'
    bl_context = ''

    def draw(self, _context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text=_('Render:'), icon='SCENE_DATA')
        col.operator(SetupRenderEngineForEevee.bl_idname, icon='SCENE')
        col.operator(ConvertMaterialsForEevee.bl_idname, icon='NODE_MATERIAL')

        col = layout.column(align=True)
        col.label(text=_('MMD to Rigify:'), icon='OUTLINER_OB_ARMATURE')
        row = col.split(factor=0.9, align=True)
        row.operator_context = 'EXEC_DEFAULT'
        row.operator(MMDArmatureAddMetarig.bl_idname, text=_('Add Metarig'), icon='ADD').is_clean_armature = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator(MMDArmatureAddMetarig.bl_idname, text=_(''), icon='WINDOW')

        row = col.split(factor=0.9, align=True)
        row.operator_context = 'EXEC_DEFAULT'
        row.operator(MMDRigifyIntegrate.bl_idname, text=_('Integrate Armatures'), icon='GROUP_BONE').is_join_armatures = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator(MMDRigifyIntegrate.bl_idname, text=_(''), icon='WINDOW')

        row = col.split(factor=0.9, align=True)
        row.operator_context = 'EXEC_DEFAULT'
        row.operator(MMDRigifyBind.bl_idname, text=_('Bind Armatures'), icon='GROUP_BONE').is_join_armatures = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator(MMDRigifyBind.bl_idname, text=_(''), icon='WINDOW')

        col = layout.column(align=True)
        col.label(text=_('Rigify to MMD:'), icon='OUTLINER_OB_ARMATURE')
        col.operator(MMDRigifyConvert.bl_idname, text=_('Convert to MMD compatible'), icon='ARMATURE_DATA')
        col.separator()
        col.operator(MMDRigifyApplyMMDRestPose.bl_idname, text=_('Apply MMD Rest Pose'))

        col.label(text=_('(Experimental) Auto-Rig to MMD:'), icon='OUTLINER_OB_ARMATURE')
        col.operator(MMDAutoRigConvert.bl_idname, text=_('Convert to MMD compatible'), icon='ARMATURE_DATA')
        col.separator()
        col.operator(MMDAutoRigApplyMMDRestPose.bl_idname, text=_('Apply MMD Rest Pose'))

        layout.label(text=_('UI Panels'))
        col = layout.column(align=True)
        col.label(text=_('World > MMD UuuNyaa Lighting Panel'), icon='WORLD')
        col.label(text=_('Material > MMD UuuNyaa Material Panel'), icon='MATERIAL')

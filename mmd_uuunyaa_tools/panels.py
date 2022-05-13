# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy

from mmd_uuunyaa_tools.checkers.operators import CheckEeveeRenderingPerformance
from mmd_uuunyaa_tools.converters.armatures.operators import (
    MMDArmatureAddMetarig, MMDAutoRigApplyMMDRestPose, MMDAutoRigConvert,
    MMDRigifyApplyMMDRestPose, MMDRigifyConvert, MMDRigifyIntegrateFocusOnMMD,
    MMDRigifyIntegrateFocusOnRigify)
from mmd_uuunyaa_tools.editors.operators import (SetupRenderEngineForEevee,
                                                 SetupRenderEngineForToonEevee,
                                                 SetupRenderEngineForWorkbench)
from mmd_uuunyaa_tools.m17n import _


class OperatorPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_operator_panel'
    bl_label = _('UuuNyaa Operator')
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'
    bl_context = ''

    def draw(self, _context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text=_('Render:'), icon='SCENE_DATA')
        grid = col.grid_flow(row_major=True, align=True)
        grid.row(align=True).operator(SetupRenderEngineForEevee.bl_idname, icon='SCENE')
        grid.row(align=True).operator(SetupRenderEngineForWorkbench.bl_idname, icon='SCENE')
        grid.row(align=True).operator(SetupRenderEngineForToonEevee.bl_idname, icon='SCENE')
        grid.row(align=True).operator(CheckEeveeRenderingPerformance.bl_idname, icon='MOD_TIME')

        col = layout.column(align=True)
        col.label(text=_('MMD to Rigify:'), icon='OUTLINER_OB_ARMATURE')
        grid = col.grid_flow(row_major=True, align=True)
        row = grid.row(align=True)
        row.operator_context = 'EXEC_DEFAULT'
        row.operator(MMDArmatureAddMetarig.bl_idname, text=_('Add Metarig'), icon='ADD').is_clean_armature = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator(MMDArmatureAddMetarig.bl_idname, text=_(''), icon='WINDOW')

        row = grid.row(align=True)
        row.operator_context = 'EXEC_DEFAULT'
        row.operator(MMDRigifyIntegrateFocusOnMMD.bl_idname, icon='GROUP_BONE').is_join_armatures = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator(MMDRigifyIntegrateFocusOnMMD.bl_idname, text=_(''), icon='WINDOW')

        row = grid.row(align=True)
        row.operator_context = 'EXEC_DEFAULT'
        row.operator(MMDRigifyIntegrateFocusOnRigify.bl_idname, icon='GROUP_BONE').is_join_armatures = True
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator(MMDRigifyIntegrateFocusOnRigify.bl_idname, text=_(''), icon='WINDOW')

        col = layout.column(align=True)
        col.label(text=_('Rigify to MMD:'), icon='OUTLINER_OB_ARMATURE')
        grid = col.grid_flow(row_major=True, align=True)
        grid.row(align=True).operator(MMDRigifyConvert.bl_idname, text=_('Convert to MMD compatible'), icon='ARMATURE_DATA')
        grid.row(align=True).operator(MMDRigifyApplyMMDRestPose.bl_idname, text=_('Apply MMD Rest Pose'))

        col.label(text=_('(Experimental) Auto-Rig to MMD:'), icon='OUTLINER_OB_ARMATURE')
        grid = col.grid_flow(row_major=True, align=True)
        grid.row(align=True).operator(MMDAutoRigConvert.bl_idname, text=_('Convert to MMD compatible'), icon='ARMATURE_DATA')
        grid.row(align=True).operator(MMDAutoRigApplyMMDRestPose.bl_idname, text=_('Apply MMD Rest Pose'))

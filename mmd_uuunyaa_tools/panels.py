# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy

from mmd_uuunyaa_tools import operators
from mmd_uuunyaa_tools.tuners import lighting_tuners, material_tuners
from mmd_uuunyaa_tools.editors.operators import MMDArmatureAddMetarig, MMDRigifyIntegrate, MMDRigifyConvert, MMDRigifyApplyMMDRestPose


class OperatorPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_operator_panel'
    bl_label = 'UuuNyaa Operator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'
    bl_context = ''

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text='Render:', icon='SCENE_DATA')
        col.operator(operators.SetupRenderEngineForEevee.bl_idname, icon='SCENE')
        col.operator(operators.ConvertMaterialsForEevee.bl_idname, icon='NODE_MATERIAL')

        col = layout.column(align=True)
        col.label(text='MMD to Rigify:', icon='OUTLINER_OB_ARMATURE')
        col.operator(MMDArmatureAddMetarig.bl_idname, text='Add Metarig', icon='ADD')
        col.operator(MMDRigifyIntegrate.bl_idname, text='Integrate Armatures', icon='GROUP_BONE')

        col = layout.column(align=True)
        col.label(text='Rigify to MMD:', icon='OUTLINER_OB_ARMATURE')
        col.operator(MMDRigifyConvert.bl_idname, text='Convert to MMD compatible', icon='ARMATURE_DATA')
        col.operator(MMDRigifyApplyMMDRestPose.bl_idname, text='Apply MMD rest pose')

        layout.label(text='UI Panels')
        col = layout.column(align=True)
        col.label(text='World > MMD UuuNyaa Lighting Panel', icon='WORLD')
        col.label(text='Material > MMD UuuNyaa Material Panel', icon='MATERIAL')

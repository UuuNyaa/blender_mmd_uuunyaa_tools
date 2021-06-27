# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
from mmd_uuunyaa_tools.editors.physics.cloth import (
    ConvertRigidBodyToClothOperator, RemoveMeshCloth, SelectMeshCloth)
from mmd_uuunyaa_tools.editors.physics.collision import (RemoveMeshCollision,
                                                         SelectMeshCollision)
from mmd_uuunyaa_tools.m17n import _
from mmd_uuunyaa_tools.utilities import import_mmd_tools

mmd_tools = import_mmd_tools()


class UuuNyaaPhysicsPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_physics'
    bl_label = _('UuuNyaa Physics')
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text=_('Relevant Selection:'), icon='RESTRICT_SELECT_OFF')
        col.operator_context = 'EXEC_DEFAULT'
        operator = col.operator('mmd_tools.rigid_body_select', text=_('Select Rigid Body'), icon='RIGID_BODY')
        operator.properties = set(['collision_group_number', 'shape'])
        col.operator(SelectMeshCollision.bl_idname, text=_('Select Collision Mesh'), icon='MOD_PHYSICS')
        col.operator(SelectMeshCloth.bl_idname, text=_('Select Cloth Mesh'), icon='MOD_CLOTH')

        col = layout.column(align=True)
        col.label(text=_('MMD Model:'), icon='OUTLINER_OB_ARMATURE')
        box = col.box()
        root_object = mmd_tools.core.model.Model.findRoot(context.active_object)
        if root_object is None:
            box.label(text=_('Not selected.'), icon='ERROR')
        else:
            mmd_root = root_object.mmd_root

            col = box.column(align=True)
            col.label(text=_('Visibility:'), icon='HIDE_OFF')
            row = col.row(align=True)
            row.prop(mmd_root, 'show_meshes', text=_('Mesh'), toggle=True)
            row.prop(mmd_root, 'show_armature', text=_('Armature'), toggle=True)
            row.prop(mmd_root, 'show_rigid_bodies', text=_('Rigid Body'), toggle=True)

            col = box.column(align=True)
            col.label(text='Converter:', icon='SHADERFX')

            row = col.split(factor=0.9, align=True)
            row.operator_context = 'EXEC_DEFAULT'
            row.operator(ConvertRigidBodyToClothOperator.bl_idname, text=_('Rigid Body to Cloth'), icon='MATCLOTH')
            row.operator_context = 'INVOKE_DEFAULT'
            row.operator(ConvertRigidBodyToClothOperator.bl_idname, text=_(''), icon='WINDOW')

        col = layout.column(align=True)
        col.label(text=_('Remove:'), icon='TRASH')
        col.operator_context = 'INVOKE_DEFAULT'
        col.operator('rigidbody.objects_remove', text=_('Remove Mesh Rigid Body'), icon='RIGID_BODY')
        col.operator(RemoveMeshCollision.bl_idname, text=_('Remove Mesh Collision'), icon='MOD_PHYSICS')
        col.operator(RemoveMeshCloth.bl_idname, text=_('Remove Mesh Cloth'), icon='MOD_CLOTH')

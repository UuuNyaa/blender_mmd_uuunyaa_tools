# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
import rna_prop_ui
from mmd_uuunyaa_tools.editors.physics.cloth import (
    ConvertRigidBodyToClothOperator, RemoveMeshCloth, SelectClothMesh)
from mmd_uuunyaa_tools.editors.physics.collision import (RemoveMeshCollision,
                                                         SelectCollisionMesh)
from mmd_uuunyaa_tools.m17n import _
from mmd_uuunyaa_tools.utilities import import_mmd_tools

mmd_tools = import_mmd_tools()


class UuuNyaaPhysicsPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_physics'
    bl_label = _('UuuNyaa Physics')
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'

    def check_prop(self, obj: bpy.types.Object):
        if 'mmd_uuunyaa_tools_show_cloths' in obj:
            return

        rna_prop_ui.rna_idprop_ui_create(
            obj, 'mmd_uuunyaa_tools_show_cloths',
            default=True,
            min=False, max=True,
            soft_min=None, soft_max=None,
            description='descriptions',
            overridable=True,
            subtype='Boolean'
        )

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        col = layout.column(align=True)
        col.label(text=_('Relevant Selection:'), icon='RESTRICT_SELECT_OFF')

        col = col.grid_flow()
        row = col.split(factor=0.9, align=True)
        row.operator_context = 'EXEC_DEFAULT'
        operator = row.operator('mmd_tools.rigid_body_select', text=_('Select Rigid Body'), icon='RIGID_BODY')
        operator.properties = set(['collision_group_number', 'shape'])
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator('rigidbody.objects_remove', text=_(''), icon='TRASH')

        row = col.split(factor=0.9, align=True)
        row.operator(SelectCollisionMesh.bl_idname, text=_('Select Collision Mesh'), icon='MOD_PHYSICS')
        row.operator(RemoveMeshCollision.bl_idname, text=_(''), icon='TRASH')

        row = col.split(factor=0.9, align=True)
        row.operator(SelectClothMesh.bl_idname, text=_('Select Cloth Mesh'), icon='MOD_CLOTH')
        row.operator(RemoveMeshCloth.bl_idname, text=_(''), icon='TRASH')

        mmd_root_object = mmd_tools.core.model.Model.findRoot(context.active_object)
        if mmd_root_object is None:
            col = layout.column(align=True)
            col.label(text=_('MMD Model is not selected.'), icon='ERROR')
        else:
            mmd_root = mmd_root_object.mmd_root

            col = layout.column(align=True)
            col.label(text=_('Visibility:'), icon='HIDE_OFF')
            row = col.grid_flow(align=True)
            row.prop(mmd_root, 'show_meshes', text=_('Mesh'), toggle=True)
            row.prop(mmd_root, 'show_armature', text=_('Armature'), toggle=True)
            row.prop(mmd_root, 'show_rigid_bodies', text=_('Rigid Body'), toggle=True)
            row.prop(mmd_root_object, 'mmd_uuunyaa_tools_show_cloths', text=_('Cloth'), toggle=True)

            col = layout.column(align=True)
            col.label(text='Converter:', icon='SHADERFX')

            row = col.split(factor=0.9, align=True)
            row.operator_context = 'EXEC_DEFAULT'
            row.operator(ConvertRigidBodyToClothOperator.bl_idname, text=_('Rigid Body to Cloth'), icon='MATCLOTH')
            row.operator_context = 'INVOKE_DEFAULT'
            row.operator(ConvertRigidBodyToClothOperator.bl_idname, text=_(''), icon='WINDOW')

    @staticmethod
    def _toggle_visibility_of_cloths(obj, context):
        mmd_root_object = mmd_tools.core.model.Model.findRoot(obj)
        mmd_model = mmd_tools.core.model.Model(mmd_root_object)
        hide = not mmd_root_object.mmd_uuunyaa_tools_show_cloths

        cloth_object: bpy.types.Object
        for cloth_object in mmd_model.cloths():
            cloth_object.hide = hide

        if hide and context.active_object is None:
            context.view_layer.objects.active = mmd_root_object

    @staticmethod
    def register():
        # pylint: disable=assignment-from-no-return
        bpy.types.Object.mmd_uuunyaa_tools_show_cloths = bpy.props.BoolProperty(
            default=True,
            update=UuuNyaaPhysicsPanel._toggle_visibility_of_cloths
        )

    @staticmethod
    def unregister():
        del bpy.types.Object.mmd_uuunyaa_tools_show_cloths

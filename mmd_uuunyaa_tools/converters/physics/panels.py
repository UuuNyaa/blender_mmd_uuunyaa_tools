# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
from mmd_uuunyaa_tools.converters.physics.cloth import (
    ConvertRigidBodyToClothOperator, RemoveMeshCloth, SelectClothMesh)
from mmd_uuunyaa_tools.converters.physics.cloth_pyramid import (
    AddPyramidMeshByBreastBoneOperator, AssignPyramidWeightsOperator,
    ConvertPyramidMeshToClothOperator)
from mmd_uuunyaa_tools.converters.physics.collision import (
    RemoveMeshCollision, SelectCollisionMesh)
from mmd_uuunyaa_tools.converters.physics.cloth_bone import StretchBoneToVertexOperator
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
        grid = col.grid_flow(row_major=True)
        row = grid.row(align=True)
        row.label(text=_('Collision Mesh'), icon='MOD_PHYSICS')
        row.operator(SelectCollisionMesh.bl_idname, text=_(''), icon='RESTRICT_SELECT_OFF')
        row.operator(RemoveMeshCollision.bl_idname, text=_(''), icon='TRASH')

        mmd_root_object = mmd_tools.core.model.Model.findRoot(context.active_object)
        if mmd_root_object is None:
            col = layout.column(align=True)
            col.label(text=_('MMD Model is not selected.'), icon='ERROR')
        else:
            mmd_root = mmd_root_object.mmd_root

            row = grid.row(align=True)
            row.label(text=_('Rigid Body'), icon='RIGID_BODY')
            row.operator_context = 'EXEC_DEFAULT'
            operator = row.operator('mmd_tools.rigid_body_select', text=_(''), icon='RESTRICT_SELECT_OFF')
            operator.properties = set(['collision_group_number', 'shape'])
            row.operator_context = 'INVOKE_DEFAULT'
            row.prop(mmd_root, 'show_rigid_bodies', toggle=True, icon_only=True, icon='HIDE_OFF' if mmd_root.show_rigid_bodies else 'HIDE_ON')
            row.operator('rigidbody.objects_remove', text=_(''), icon='TRASH')

            row = grid.row(align=True)
            row.label(text=_('Cloth Mesh'), icon='MOD_CLOTH')
            row.operator(SelectClothMesh.bl_idname, text=_(''), icon='RESTRICT_SELECT_OFF')
            row.prop(mmd_root_object, 'mmd_uuunyaa_tools_show_cloths', toggle=True, icon_only=True, icon='HIDE_OFF' if mmd_root_object.mmd_uuunyaa_tools_show_cloths else 'HIDE_ON')
            row.operator(RemoveMeshCloth.bl_idname, text=_(''), icon='TRASH')

            col = layout.column(align=True)
            col.label(text=_('Converter:'), icon='SHADERFX')

            row = col.row(align=True)
            row.operator_context = 'EXEC_DEFAULT'
            row.operator(ConvertRigidBodyToClothOperator.bl_idname, text=_('Rigid Body to Cloth'), icon='MATCLOTH')
            row.operator_context = 'INVOKE_DEFAULT'
            row.operator(ConvertRigidBodyToClothOperator.bl_idname, text=_(''), icon='WINDOW')

        col = layout.column(align=True)
        col.label(text=_('Pyramid Cloth:'), icon='MESH_CONE')
        grid = col.grid_flow(row_major=True, align=True)
        grid.row(align=True).operator(AddPyramidMeshByBreastBoneOperator.bl_idname, text=_('Add Pyramid'), icon='CONE')
        grid.row(align=True).operator(ConvertPyramidMeshToClothOperator.bl_idname, text=_('Pyramid to Cloth'), icon='MOD_CLOTH')
        grid.row(align=True).operator(AssignPyramidWeightsOperator.bl_idname, text=_('Repaint Weight'), icon='WPAINT_HLT')

        col = layout.column(align=True)
        col.label(text=_('Misc:'), icon='BLENDER')
        grid = col.grid_flow(row_major=True)
        grid.row(align=True).operator(StretchBoneToVertexOperator.bl_idname, text=_('Stretch Bone to Vertex'), icon='CONSTRAINT_BONE')

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

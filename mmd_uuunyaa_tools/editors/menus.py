# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
from mmd_uuunyaa_tools.editors.operators import (RemoveUnusedShapeKeys,
                                                 RemoveUnusedVertexGroups,
                                                 SelectShapeKeyTargetVertices)
from mmd_uuunyaa_tools.m17n import _


class RemoveUnusedVertexGroupsMenu(bpy.types.Menu):
    bl_idname = 'VGROUP_MT_mmd_uuunyaa_tools_remove_unused_vertex_groups'
    bl_label = _('MMD UuuNyaa')

    def draw(self, _):
        pass

    @staticmethod
    def draw_menu(this, _):
        this.layout.operator(RemoveUnusedVertexGroups.bl_idname)

    @staticmethod
    def register():
        bpy.types.MESH_MT_vertex_group_context_menu.append(RemoveUnusedVertexGroupsMenu.draw_menu)

    @staticmethod
    def unregister():
        bpy.types.MESH_MT_vertex_group_context_menu.remove(RemoveUnusedVertexGroupsMenu.draw_menu)


class SelectShapeKeyTargetVerticesMenu(bpy.types.Menu):
    bl_idname = 'SHAPEKEY_MT_mmd_uuunyaa_tools_select_shape_key_target_vertices'
    bl_label = _('MMD UuuNyaa')

    def draw(self, _):
        pass

    @staticmethod
    def draw_menu(this, _):
        this.layout.operator(SelectShapeKeyTargetVertices.bl_idname)

    @staticmethod
    def register():
        bpy.types.MESH_MT_shape_key_context_menu.append(SelectShapeKeyTargetVerticesMenu.draw_menu)

    @staticmethod
    def unregister():
        bpy.types.MESH_MT_shape_key_context_menu.remove(SelectShapeKeyTargetVerticesMenu.draw_menu)


class RemoveUnusedShapeKeysMenu(bpy.types.Menu):
    bl_idname = 'VGROUP_MT_mmd_uuunyaa_tools_remove_unused_shape_keys'
    bl_label = _('MMD UuuNyaa')

    def draw(self, context):
        pass

    @staticmethod
    def draw_menu(this, _):
        this.layout.operator(RemoveUnusedShapeKeys.bl_idname)

    @staticmethod
    def register():
        bpy.types.MESH_MT_shape_key_context_menu.append(RemoveUnusedShapeKeysMenu.draw_menu)

    @staticmethod
    def unregister():
        bpy.types.MESH_MT_shape_key_context_menu.remove(RemoveUnusedShapeKeysMenu.draw_menu)

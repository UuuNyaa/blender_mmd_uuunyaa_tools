# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy

from mmd_uuunyaa_tools.operators import (RemoveUnusedShapeKeys,
                                         RemoveUnusedVertexGroups,
                                         SelectRelatedBones,
                                         SelectRelatedObjects,
                                         SelectRelatedPoseBones,
                                         SelectShapeKeyTargetVertices)


class SelectRelatedObjectsMenu(bpy.types.Menu):
    bl_idname = 'VIEW3D_MT_mmd_uuunyaa_tools_select_related_objects'
    bl_label = 'MMD UuuNyaa'

    def draw(self, context):
        pass

    @staticmethod
    def draw_object_menu(this, _):
        this.layout.operator(SelectRelatedObjects.bl_idname)

    @staticmethod
    def draw_bone_menu(this, _):
        this.layout.operator(SelectRelatedBones.bl_idname)

    @staticmethod
    def draw_pose_bone_menu(this, _):
        this.layout.operator(SelectRelatedPoseBones.bl_idname)

    @staticmethod
    def register():
        bpy.types.VIEW3D_MT_select_object.append(SelectRelatedObjectsMenu.draw_object_menu)
        bpy.types.VIEW3D_MT_select_edit_armature.append(SelectRelatedObjectsMenu.draw_bone_menu)
        bpy.types.VIEW3D_MT_select_pose.append(SelectRelatedObjectsMenu.draw_pose_bone_menu)

    @staticmethod
    def unregister():
        bpy.types.VIEW3D_MT_select_pose.remove(SelectRelatedObjectsMenu.draw_pose_bone_menu)
        bpy.types.VIEW3D_MT_select_edit_armature.remove(SelectRelatedObjectsMenu.draw_bone_menu)
        bpy.types.VIEW3D_MT_select_object.remove(SelectRelatedObjectsMenu.draw_object_menu)


class RemoveUnusedVertexGroupsMenu(bpy.types.Menu):
    bl_idname = 'VGROUP_MT_mmd_uuunyaa_tools_remove_unused_vertex_groups'
    bl_label = 'MMD UuuNyaa'

    def draw(self, context):
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
    bl_label = 'MMD UuuNyaa'

    def draw(self, context):
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
    bl_label = 'MMD UuuNyaa'

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

# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy

from mmd_uuunyaa_tools.operators import SelectRelatedBones, SelectRelatedObjects, SelectRelatedPoseBones


class ObjectSelectMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_mmd_uuunyaa_tools_select_object"
    bl_label = "MMD UuuNyaa"

    def draw(self, context):
        layout = self.layout
        layout.operator(SelectRelatedObjects.bl_idname)

    @staticmethod
    def object_menu_func(this, context):
        this.layout.menu(ObjectSelectMenu.bl_idname)

    @staticmethod
    def register():
        bpy.types.VIEW3D_MT_select_object.append(ObjectSelectMenu.object_menu_func)

    @staticmethod
    def unregister():
        bpy.types.VIEW3D_MT_select_object.remove(ObjectSelectMenu.object_menu_func)


class BoneSelectMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_mmd_uuunyaa_tools_select_bone"
    bl_label = "MMD UuuNyaa"

    def draw(self, context):
        layout = self.layout
        layout.operator(SelectRelatedBones.bl_idname)

    @staticmethod
    def bone_menu_func(this, context):
        this.layout.menu(BoneSelectMenu.bl_idname)

    @staticmethod
    def register():
        bpy.types.VIEW3D_MT_select_edit_armature.append(BoneSelectMenu.bone_menu_func)

    @staticmethod
    def unregister():
        bpy.types.VIEW3D_MT_select_edit_armature.remove(BoneSelectMenu.bone_menu_func)


class PoseBoneSelectMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_mmd_uuunyaa_tools_select_pose_bone"
    bl_label = "MMD UuuNyaa"

    def draw(self, context):
        layout = self.layout
        layout.operator(SelectRelatedPoseBones.bl_idname)

    @staticmethod
    def pose_bone_menu_func(this, context):
        this.layout.menu(PoseBoneSelectMenu.bl_idname)

    @staticmethod
    def register():
        bpy.types.VIEW3D_MT_select_pose.append(PoseBoneSelectMenu.pose_bone_menu_func)

    @staticmethod
    def unregister():
        bpy.types.VIEW3D_MT_select_pose.remove(PoseBoneSelectMenu.pose_bone_menu_func)

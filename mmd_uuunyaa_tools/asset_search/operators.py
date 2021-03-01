# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
from mmd_uuunyaa_tools import PACKAGE_NAME
from mmd_uuunyaa_tools.asset_search.assets import ASSETS
from mmd_uuunyaa_tools.asset_search.cache import CONTENT_CACHE


class ReloadAssetJsons(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.reload_asset_jsons'
    bl_label = 'Reload Asset JSONs'
    bl_description = 'Reload asset JSONs.'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        asset_jsons_folder = context.preferences.addons[PACKAGE_NAME].preferences.asset_jsons_folder
        ASSETS.reload(asset_jsons_folder)

        return {'FINISHED'}


class DeleteCachedFiles(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.delete_cached_files'
    bl_label = 'Delete Asset Cached Files'
    bl_description = 'Delete cached files.'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        CONTENT_CACHE.delete_cache_folder()
        return {'FINISHED'}

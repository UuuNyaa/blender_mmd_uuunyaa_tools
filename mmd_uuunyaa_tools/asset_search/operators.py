# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import ast
import importlib
import json
import os

import bpy
import requests
from mmd_uuunyaa_tools import PACKAGE_NAME, PACKAGE_PATH
from mmd_uuunyaa_tools.asset_search.assets import ASSETS
from mmd_uuunyaa_tools.asset_search.cache import CONTENT_CACHE


def load_cat_asset_json():
    namespace = 'cat_asset_json'
    loader = importlib.machinery.SourceFileLoader(
        namespace,
        os.path.join(PACKAGE_PATH, 'externals', 'blender_mmd_assets', 'cat_asset_json.py')
    )
    return loader.load_module(namespace)


class ReloadAssetJsons(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.reload_asset_jsons'
    bl_label = 'Reload Asset JSONs'
    bl_description = 'Reload asset JSONs.'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        asset_jsons_folder = context.preferences.addons[PACKAGE_NAME].preferences.asset_jsons_folder
        ASSETS.reload(asset_jsons_folder)

        return {'FINISHED'}


class UpdateAssetJson(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.update_asset_json'
    bl_label = 'Update Assets JSON'
    bl_description = 'Update assets JSON.'
    bl_options = {'INTERNAL'}

    repo: bpy.props.StringProperty(default='UuuNyaa/blender_mmd_assets')
    query: bpy.props.StringProperty(default="{'state': 'open', 'milestone': 1, 'labels': 'Official'}")
    output_json: bpy.props.StringProperty(default='assets.json')

    def execute(self, context):
        query = ast.literal_eval(self.query)
        cat_asset_json = load_cat_asset_json()

        session = requests.Session()
        assets = cat_asset_json.wrap_assets(cat_asset_json.fetch_assets(session, self.repo, query))

        with open(os.path.join(PACKAGE_PATH, 'asset_jsons', self.output_json), mode='wt', encoding='utf-8') as f:
            json.dump(assets, f, ensure_ascii=False, indent=2)

        return {'FINISHED'}


class UpdateDebugAssetJson(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.update_debug_asset_json'
    bl_label = 'Update Debug Asset JSON'
    bl_description = 'Update debug asset JSON.'
    bl_options = {'INTERNAL'}

    repo: bpy.props.StringProperty(default='UuuNyaa/blender_mmd_assets')
    issue_number: bpy.props.IntProperty()
    output_json: bpy.props.StringProperty(default='ZDEBUG.json')

    def execute(self, context):
        json_path = os.path.join(PACKAGE_PATH, 'asset_jsons', self.output_json)

        cat_asset_json = load_cat_asset_json()

        session = requests.Session()
        assets = cat_asset_json.wrap_assets([
            cat_asset_json.fetch_asset(session, self.repo, self.issue_number)
        ])

        with open(json_path, mode='wt', encoding='utf-8') as f:
            json.dump(assets, f, ensure_ascii=False, indent=2)

        return {'FINISHED'}


class DeleteDebugAssetJson(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.delete_debug_asset_json'
    bl_label = 'Delete Debug Asset JSON'
    bl_description = 'Delete debug asset JSON.'
    bl_options = {'INTERNAL'}

    delete_json: bpy.props.StringProperty(default='ZDEBUG.json')

    def execute(self, context):
        json_path = os.path.join(PACKAGE_PATH, 'asset_jsons', self.delete_json)

        if not os.path.exists(json_path):
            self.report(type={'INFO'}, message=f'{self.delete_json} does not exist.')
            return {'CANCELLED'}

        os.remove(json_path)
        return {'FINISHED'}


class DeleteCachedFiles(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.delete_cached_files'
    bl_label = 'Delete Asset Cached Files'
    bl_description = 'Delete cached files.'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        CONTENT_CACHE.delete_cache_folder()
        return {'FINISHED'}

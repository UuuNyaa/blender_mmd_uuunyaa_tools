# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import os
import pathlib
import tempfile

import bpy

from mmd_uuunyaa_tools import utilities
from mmd_uuunyaa_tools.asset_search.operators import DeleteCachedFiles
from mmd_uuunyaa_tools.asset_search.assets import AssetUpdater


class MMDUuuNyaaToolsAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    asset_search_results_max_display_count: bpy.props.IntProperty(
        name='Asset Search Results Max. Display Count',
        description='Larger value is slower',
        min=10,
        soft_max=200,
        default=50,
    )

    asset_jsons_folder: bpy.props.StringProperty(
        name='Asset JSONs Folder',
        description='Path to asset list JSON files',
        subtype='DIR_PATH',
        default=os.path.join(os.path.dirname(__file__), 'asset_jsons')
    )

    asset_json_update_repo: bpy.props.StringProperty(
        name='Asset JSON Update Repo',
        description='Specify the github repository which to retrieve the assets',
        default=AssetUpdater.default_repo
    )

    asset_json_update_query: bpy.props.StringProperty(
        name='Asset JSON Update Query',
        description='Specify the filter conditions for retrieving assets',
        default=AssetUpdater.default_query
    )

    asset_json_update_on_startup_enabled: bpy.props.BoolProperty(
        name='Asset JSON Auto Update on Startup',
        default=True
    )

    asset_cache_folder: bpy.props.StringProperty(
        name="Asset Cache Folder",
        description=('Directory path to download cache'),
        subtype='DIR_PATH',
        default=os.path.join(tempfile.gettempdir(), 'mmd_uuunyaa_tools_cache'),
    )

    asset_max_cache_size: bpy.props.IntProperty(
        name='Asset Max. Cache Size (MB)',
        description='Maximum size (Mega bytes) of the cache folder',
        min=100,
        soft_max=1_000_000,
        default=10_000,
    )

    asset_extract_root_folder: bpy.props.StringProperty(
        name='Asset Extract Root Folder',
        description='Path to extract the downloaded assets',
        subtype='DIR_PATH',
        default=os.path.join(pathlib.Path.home(), 'BlenderAssets')
    )

    asset_extract_folder: bpy.props.StringProperty(
        name='Asset Extract Folder',
        description='Path to assets. Create it under the Asset Extract Root Folder.\n'
        'The following variables are available: {id}, {type}, {name}, {aliases[en]}, {aliases[ja]}',
        default='{type}/{id}.{name}'
    )

    asset_extract_json: bpy.props.StringProperty(
        name='Asset Extract Json',
        description='Name to assets marker JSON. Create it under the Asset Extract Folder.\n'
        'The presence of this file is used to determine the existence of the asset.\n'
        'The following variables are available: {id}, {type}, {name}, {aliases[en]}, {aliases[ja]}',
        default='{id}.json'
    )

    def draw(self, _):
        layout = self.layout  # pylint: disable=no-member

        col = layout.box().column()
        col.prop(self, 'asset_search_results_max_display_count')

        col = layout.box().column()
        col.prop(self, 'asset_jsons_folder')

        row = col.split(factor=0.95, align=True)
        row.prop(self, 'asset_json_update_repo')
        row.operator('wm.url_open', text='Browse Assets', icon='URL').url = f'https://github.com/{self.asset_json_update_repo}/issues'

        row = col.split(factor=0.95, align=True)
        row.prop(self, 'asset_json_update_query')
        row.operator('wm.url_open', text='Query Examples', icon='URL').url = 'https://github.com/UuuNyaa/blender_mmd_uuunyaa_tools/wiki/How-to-add-a-new-asset#query-examples'

        col.prop(self, 'asset_json_update_on_startup_enabled')

        col = layout.box().column()
        col.prop(self, 'asset_cache_folder')

        usage = col.split(align=True, factor=0.24)
        usage.label(text='Asset Cache Usage:')
        usage_row = usage.column(align=True)
        usage_row.alignment = 'RIGHT'

        cache_folder_size = sum(f.stat().st_size for f in pathlib.Path(self.asset_cache_folder).glob('**/*') if f.is_file())
        usage_row.label(text=f'{utilities.to_human_friendly_text(cache_folder_size)}B')

        col.prop(self, 'asset_max_cache_size')

        col.operator(DeleteCachedFiles.bl_idname)

        col = layout.box().column()
        col.prop(self, 'asset_extract_root_folder')
        col.prop(self, 'asset_extract_folder')
        col.prop(self, 'asset_extract_json')

# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import os
import pathlib
import tempfile

import bpy

from mmd_uuunyaa_tools import utilities
from mmd_uuunyaa_tools.asset_search.operators import DeleteCachedFiles, ReloadAssetJsons


class MMDUuuNyaaToolsAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    cache_folder: bpy.props.StringProperty(
        name="Cache Folder",
        description=('Directory path to download cache.'),
        subtype='DIR_PATH',
        default=os.path.join(tempfile.gettempdir(), 'mmd_uuunyaa_tools_cache'),
    )

    max_cache_size: bpy.props.IntProperty(
        name='Max. Cache Size (MB)',
        description='Maximum size (Mega bytes) of the cache folder.',
        min=100,
        soft_max=1_000_000,
        default=10_000,
    )

    asset_jsons_folder: bpy.props.StringProperty(
        name='Asset JSONs Folder',
        description='Path to asset list JSON files.',
        subtype='DIR_PATH',
        default=os.path.join(os.path.dirname(__file__), 'asset_jsons')
    )

    asset_extract_folder: bpy.props.StringProperty(
        name='Asset Extract Folder',
        description='Path to extract the downloaded assets.',
        subtype='DIR_PATH',
        default=os.path.join(pathlib.Path.home(), 'BlenderAssets')
    )

    asset_extract_name: bpy.props.StringProperty(
        name='Asset Extract Name',
        description='Name to assets. Create it under the Asset Extract Folder.\n'
        'The following variables are available: {id}, {type}, {name}, {aliases_en}, {aliases_ja}',
        default='{type}/{id}.{name}'
    )

    def draw(self, context):
        layout = self.layout

        row = layout.split(factor=0.1)
        row.label(text='Disk Cache:')
        col = row.box().column(align=True)
        col.prop(self, 'cache_folder', text='Folder')

        usage = col.split(align=True, factor=0.24)
        usage.label(text='Usage:')
        usage_row = usage.column(align=True)
        usage_row.alignment = 'RIGHT'

        cache_folder_size = sum(f.stat().st_size for f in pathlib.Path(self.cache_folder).glob('**/*') if f.is_file())
        usage_row.label(text=f'{utilities.to_human_friendly_text(cache_folder_size)}B')

        col.prop(self, 'max_cache_size')

        col.separator()
        col.operator(DeleteCachedFiles.bl_idname)

        row = layout.split(factor=0.1)
        row.label(text='Assets:')
        col = row.box().column(align=True)
        col.prop(self, 'asset_extract_folder')
        col.prop(self, 'asset_extract_name')

        col.separator()
        col.prop(self, 'asset_jsons_folder')
        col.operator(ReloadAssetJsons.bl_idname)

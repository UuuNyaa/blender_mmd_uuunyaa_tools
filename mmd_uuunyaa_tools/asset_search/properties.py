# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from typing import Dict

import bpy
from mmd_uuunyaa_tools.asset_search.assets import ASSETS, AssetType


def update_search_query(property, context):
    if context.scene.mmd_uuunyaa_tools_asset_search.query.is_updating:
        return

    bpy.ops.mmd_uuunyaa_tools.asset_search()


class TagItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(options={'SKIP_SAVE'})
    enabled: bpy.props.BoolProperty(update=update_search_query, options={'SKIP_SAVE'})


class AssetItem(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    thumbnail_filepath: bpy.props.StringProperty()


class AssetSearchResult(bpy.types.PropertyGroup):
    count: bpy.props.IntProperty(options={'SKIP_SAVE'})
    hit_count: bpy.props.IntProperty(options={'SKIP_SAVE'})
    asset_items: bpy.props.CollectionProperty(type=AssetItem, options={'SKIP_SAVE'})
    update_time: bpy.props.IntProperty(options={'SKIP_SAVE'})


class AssetSearchQuery(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        update=update_search_query,
        options={'SKIP_SAVE'},
        items=[(t.name, t.value, '') for t in AssetType],
        default=AssetType.ALL.name
    )
    text: bpy.props.StringProperty(update=update_search_query, options={'SKIP_SAVE'})
    is_cached: bpy.props.BoolProperty(update=update_search_query, options={'SKIP_SAVE'})
    tags: bpy.props.CollectionProperty(type=TagItem, options={'SKIP_SAVE'})
    tags_index: bpy.props.IntProperty(options={'SKIP_SAVE'})
    is_updating: bpy.props.BoolProperty(options={'SKIP_SAVE'})


class AssetSearchProperties(bpy.types.PropertyGroup):
    query: bpy.props.PointerProperty(type=AssetSearchQuery, options={'SKIP_SAVE'})
    result: bpy.props.PointerProperty(type=AssetSearchResult, options={'SKIP_SAVE'})

    @staticmethod
    def register():
        bpy.types.Scene.mmd_uuunyaa_tools_asset_search = bpy.props.PointerProperty(type=AssetSearchProperties)

    @staticmethod
    def unregister():
        del bpy.types.Scene.mmd_uuunyaa_tools_asset_search


class AssetOperatorProperties(bpy.types.PropertyGroup):
    repo: bpy.props.StringProperty(default='UuuNyaa/blender_mmd_assets')
    query: bpy.props.StringProperty(default="{'state': 'open', 'milestone': 1, 'labels': 'Official'}")
    output_json: bpy.props.StringProperty(default='assets.json')

    debug_expanded: bpy.props.BoolProperty(default=False)
    debug_issue_number: bpy.props.IntProperty(default=1)

    @staticmethod
    def register():
        bpy.types.Scene.mmd_uuunyaa_tools_asset_operator = bpy.props.PointerProperty(type=AssetOperatorProperties)

    @staticmethod
    def unregister():
        del bpy.types.Scene.mmd_uuunyaa_tools_asset_operator

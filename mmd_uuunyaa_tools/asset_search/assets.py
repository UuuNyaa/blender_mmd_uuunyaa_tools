import functools
import os
import tempfile
import time
from typing import List

import bpy
import bpy.utils.previews
from mmd_uuunyaa_tools.asset_search import AssetDescription, ASSETS, CONTENT_STORE
from mmd_uuunyaa_tools.asset_search.store import Content, ContentStore, Task
from mmd_uuunyaa_tools.utilities import to_human_friendly_text, to_int32


class AddAssetThumbnail(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.add_asset_thumbnail'
    bl_label = 'Add Asset Item'
    bl_options = {'UNDO_GROUPED', 'INTERNAL'}

    asset_id: bpy.props.StringProperty()
    update_time: bpy.props.IntProperty()

    def execute(self, context):
        search_result = context.scene.mmd_uuunyaa_tools_asset_search.result
        if search_result.update_time != self.update_time:
            return {'FINISHED'}

        asset_item = search_result.asset_items.add()
        asset_item.id = self.asset_id
        return {'FINISHED'}


class AssetSearch(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.asset_search'
    bl_label = 'Search Asset'
    bl_options = {'UNDO_GROUPED', 'INTERNAL'}

    def _on_thumbnail_fetched(self, context, region, update_time, asset, content):
        print(f'done: {asset.name}, {asset.id}, {content.state}, {content.id}, {update_time}, {context.scene.mmd_uuunyaa_tools_asset_search.result.update_time}')
        search_result = context.scene.mmd_uuunyaa_tools_asset_search.result
        if search_result.update_time != update_time:
            return

        asset_item = search_result.asset_items.add()
        asset_item.id = asset.id

        global PREVIEWS
        if asset.id not in PREVIEWS:
            PREVIEWS.load(asset.id, content.filepath, 'IMAGE')

        region.tag_redraw()

    def execute(self, context):
        query = context.scene.mmd_uuunyaa_tools_asset_search.query
        query_type = query.type
        query_text = query.text.lower()
        query_tags = query.tags
        query_is_cached = query.is_cached

        enabled_tag_names = {tag.name for tag in query_tags if tag.enabled}
        enabled_tag_count = len(enabled_tag_names)

        search_results: List[AssetDescription] = []
        search_results = [
            asset for asset in ASSETS.values() if (
                query_type == asset.type.name
                and enabled_tag_count == len(asset.tags & enabled_tag_names)
                and query_text in asset.keywords
                and (CONTENT_STORE.try_get_content(asset.download_url) is not None if query_is_cached else True)
            )
        ]

        update_time = to_int32(time.time_ns() >> 10)
        result = context.scene.mmd_uuunyaa_tools_asset_search.result
        result.count = len(search_results)
        result.asset_items.clear()
        result.update_time = update_time

        for asset in search_results:
            CONTENT_STORE.async_get_content(asset.thumbnail_url, functools.partial(self._on_thumbnail_fetched, context, context.region, update_time, asset))

        return {'FINISHED'}


def label_multiline(layout, text='', width=0):
    if text.strip() == '':
        return

    threshold = int(width / 5.5) if width > 0 else 35
    for line in text.split('\n'):
        while len(line) > threshold:
            space_index = line.rfind(' ', 0, threshold)
            layout.label(text=line[:space_index])
            line = line[space_index:].lstrip()
        layout.label(text=line)


class AssetDownload(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.asset_download'
    bl_label = 'Download Asset'
    bl_options = {'REGISTER', 'INTERNAL'}

    asset_id: bpy.props.StringProperty()

    def __on_fetched(self, context, asset, content):
        print(f'done: {asset.name}, {asset.id}, {content.state}, {content.id}')

    def execute(self, context):
        print(f'do: {self.bl_idname}, {self.asset_id}')
        asset = ASSETS[self.asset_id]
        CONTENT_STORE.async_get_content(asset.download_url, functools.partial(self.__on_fetched, context, asset))
        return {'FINISHED'}


class AssetImport(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.asset_import'
    bl_label = 'Import Asset'
    bl_options = {'REGISTER', 'UNDO'}

    asset_id: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print(f'do: {self.bl_idname}')
        return {'FINISHED'}


class AssetDetailPopup(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.asset_detail_popup'
    bl_label = 'Popup Asset Detail'
    bl_options = {'REGISTER', 'INTERNAL'}

    asset_id: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        print(f'do: {self.bl_idname}')
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=600)

    def draw(self, context):
        asset = ASSETS[self.asset_id]

        layout = self.layout

        def draw_titled_label(layout, title, text, split_factor=0.11):
            split = layout.split(factor=split_factor)
            split.alignment = 'RIGHT'
            split.label(text=title)
            label_multiline(split.column(align=True), text=text, width=int(600*(1-split_factor)))

        self.asset_name = asset.name

        col = layout.column(align=True)
        draw_titled_label(col, title='Name:', text=asset.name)
        draw_titled_label(col, title='Aliases:', text=', '.join([p for p in asset.aliases.values()]))
        draw_titled_label(col, title='Tags:', text=asset.tags_text())
        draw_titled_label(col, title='Updated at:', text=asset.updated_at.strftime('%Y-%m-%d %H:%M:%S %Z'))
        draw_titled_label(col, title='Note:', text=asset.note)

        content = CONTENT_STORE.try_get_content(asset.download_url)
        if content is not None:
            if content.state is Content.State.STORED:
                draw_titled_label(col, title='File:', text=f'{content.filepath}\n{to_human_friendly_text(content.length)}B   ({content.type})')
                op = layout.operator('mmd_tools.import_model', text='Import', icon='IMPORT')
                f = op.files.add()
                f.name = os.path.basename(content.filepath)
                op.directory = os.path.dirname(content.filepath)

            if content.state is Content.State.FAILED:
                layout.operator(AssetDownload.bl_idname, text='Retry', icon='FILE_REFRESH').asset_id = asset.id
        else:
            task = CONTENT_STORE.try_get_task(asset.download_url)
            if task is None:
                layout.operator(AssetDownload.bl_idname, text='Download', icon='TRIA_DOWN_BAR').asset_id = asset.id

            elif task.state is Task.State.QUEUING:
                draw_titled_label(layout, title='File:', text=f'Download waiting...')
                layout.operator(AssetDownload.bl_idname, text='Cancel', icon='CANCEL').asset_id = asset.id

            elif task.state is Task.State.RUNNING:
                draw_titled_label(layout, title='File:', text=f'Downloading {to_human_friendly_text(task.fetched_size)}B / {to_human_friendly_text(task.content_length)}B')
                layout.operator(AssetDownload.bl_idname, text=f'Cancel', icon='CANCEL').asset_id = asset.id


class AssetSearchQueryTags(bpy.types.UIList):
    bl_idname = 'UUUNYAA_UL_mmd_uuunyaa_tools_asset_search_query_tags'

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, 'enabled', text=item.name, index=index)


class AssetSearchPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_mmd_uuunyaa_tools_asset_search'
    bl_label = 'UuuNyaa Asset Search'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'

    def draw(self, context):
        search = context.scene.mmd_uuunyaa_tools_asset_search
        query = search.query
        layout = self.layout

        layout.prop(query, 'type', text='Asset type')
        layout.prop(query, 'text', text='Query', icon='VIEWZOOM')
        if query.tags is not None:
            col = layout.column()
            row = col.row()
            row.label(text='Tags:')
            row = row.row()
            row.alignment = 'RIGHT'
            row.prop(query, 'is_cached', text='Cached')
            col.template_list(AssetSearchQueryTags.bl_idname, '', query, 'tags', query, 'tags_index', type='GRID', columns=3, rows=2)
            row = col.row()

        row = layout.row()
        row.alignment = 'RIGHT'
        row.label(text=f'{search.result.count} results')

        asset_items = context.scene.mmd_uuunyaa_tools_asset_search.result.asset_items

        global PREVIEWS

        grid = layout.grid_flow(row_major=True)
        for asset_item in asset_items:
            asset = ASSETS[asset_item.id]

            content = CONTENT_STORE.try_get_content(asset.download_url)
            if content is not None:
                if content.state is Content.State.STORED:
                    icon = 'SOLO_ON'
                if content.state is Content.State.FAILED:
                    icon = 'ERROR'
            else:
                task = CONTENT_STORE.try_get_task(asset.download_url)
                if task is None:
                    icon = 'NONE'
                else:
                    icon = 'SOLO_OFF'

            box = grid.box().column(align=True)
            box.template_icon(PREVIEWS[asset.id].icon_id, scale=6.0)
            box.operator(AssetDetailPopup.bl_idname, text=asset.name, icon=icon).asset_id = asset.id

        if search.result.count > len(asset_items):
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text='Loading...')
            return

    @staticmethod
    def register():
        global PREVIEWS
        PREVIEWS = bpy.utils.previews.new()

    @staticmethod
    def unregister():
        global PREVIEWS
        if PREVIEWS is not None:
            bpy.utils.previews.remove(PREVIEWS)

import bpy
from mmd_uuunyaa_tools import PACKAGE_NAME
from mmd_uuunyaa_tools.asset_search import ASSETS


class ReloadAssetJsons(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.reload_asset_jsons'
    bl_label = 'Reload Asset JSONs'
    bl_description = 'Reload asset JSONs.'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        asset_jsons_folder = context.preferences.addons[PACKAGE_NAME].preferences.asset_jsons_folder
        ASSETS.reload(asset_jsons_folder)

        result = context.scene.mmd_uuunyaa_tools_asset_search.result
        result.count = 0
        result.asset_items.clear()
        result.update_time = 0

        return {'FINISHED'}


class DeleteCachedFiles(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.delete_cached_files'
    bl_label = 'Delete Cached Files'
    bl_description = 'Delete cached files.'
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.object.active_material

    def execute(self, context):
        return {'FINISHED'}

# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
from bpy.types import ShaderNodeGroup, ShaderNodeValue
from mmd_uuunyaa_tools.tuners import (lighting_tuners, material_tuners,
                                      operators)
from mmd_uuunyaa_tools.tuners.utilities import NodeUtilities


class SkyPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_sky_panel'
    bl_label = 'MMD UuuNyaa Sky'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'world'

    @classmethod
    def poll(cls, context):
        return context.scene.world is not None

    def draw(self, context: bpy.types.Context):
        world: bpy.types.World = context.scene.world

        utilities = NodeUtilities(world.node_tree)

        layout = self.layout

        node_frame = utilities.find_node_frame()
        if node_frame is None:
            layout.label(text='UuuNyaa World not found.')
            return

        scene_has_irradiance_volumes = self._scene_has_irradiance_volumes()
        if not scene_has_irradiance_volumes:
            layout.label(text='IrradianceVolume not found. Please add it.', icon='ERROR')

        self._draw_setting_node_properties(utilities, layout, node_frame)

        col = layout.column(align=True)
        col.label(text='for Eevee lighting, check Render Properties.')

        if not scene_has_irradiance_volumes:
            return

        col.operator('scene.light_cache_bake', text='Bake Indirect Lighting', icon='RENDER_STILL')

    @staticmethod
    def _scene_has_irradiance_volumes():
        obj: bpy.types.Object
        for obj in bpy.data.objects:
            if obj.type != 'LIGHT_PROBE':
                continue

            light_probe = obj.data
            if light_probe.type == 'GRID':
                return True

        return False

    def _draw_setting_node_properties(self, utilities, layout, node_frame):
        for node in utilities.list_nodes(node_frame=node_frame):
            if isinstance(node, ShaderNodeGroup):
                pass
            elif utilities.is_setting_node(node):
                pass
            else:
                continue
            col = layout.box().column(align=True)
            col.label(text=node.label)
            if isinstance(node, ShaderNodeValue):
                for node_output in node.outputs:
                    col.prop(node_output, 'default_value', text=node_output.name)
            else:
                for node_input in node.inputs:
                    if node_input.is_linked:
                        continue
                    col.prop(node_input, 'default_value', text=node_input.name)


class LightingPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_lighting_panel'
    bl_label = 'MMD UuuNyaa Lighting'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'world'

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        mmd_uuunyaa_tools_lighting = context.collection.mmd_uuunyaa_tools_lighting

        layout = self.layout
        col = layout.column(align=True)

        # Previews
        row = col.row()
        row.template_icon_view(mmd_uuunyaa_tools_lighting, 'thumbnails', show_labels=True)

        # Lighting Name
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=row.enum_item_name(mmd_uuunyaa_tools_lighting, 'thumbnails', mmd_uuunyaa_tools_lighting.thumbnails))

        utilities = lighting_tuners.LightingUtilities(context.collection)
        lighting = utilities.find_active_lighting()
        if lighting is None:
            return

        layout.prop(lighting, 'location')
        layout.prop(lighting, 'rotation_euler')
        layout.prop(lighting, 'scale')

        row = layout.row(align=False)
        row.operator(operators.FreezeLighting.bl_idname)


class MaterialPanel(bpy.types.Panel):
    bl_idname = 'UUUNYAA_PT_material_panel'
    bl_label = 'MMD UuuNyaa Material'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj.active_material and obj.mmd_type == 'NONE'

    def draw(self, context):
        material = context.active_object.active_material
        mmd_uuunyaa_tools_material = bpy.context.material.mmd_uuunyaa_tools_material

        layout = self.layout
        col = layout.column(align=True)

        # Previews
        row = col.row()
        row.template_icon_view(mmd_uuunyaa_tools_material, 'thumbnails', show_labels=True)

        # Material Name
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=row.enum_item_name(mmd_uuunyaa_tools_material, 'thumbnails', mmd_uuunyaa_tools_material.thumbnails))

        utilities = material_tuners.MaterialUtilities(material)
        node_frame = utilities.find_node_frame()
        if node_frame is None:
            return

        for node in utilities.list_nodes(node_type=bpy.types.ShaderNodeGroup, node_frame=node_frame):
            layout.label(text=node.label)
            for node_input in node.inputs:
                if node_input.is_linked:
                    continue
                layout.prop(node_input, 'default_value', text=node_input.name)

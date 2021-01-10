# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
from mmd_uuunyaa_tools import material_tuner
from mmd_uuunyaa_tools import lighting_tuner
from mmd_uuunyaa_tools import operators


class ObjectPanel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_mmd_uuunyaa_tools_object'
    bl_label = 'UuuNyaa Operator'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MMD'
    bl_context = ''

    def draw(self, context):
        layout = self.layout

        layout = self.layout

        col = layout.column(align=True)
        col.operator(operators.SetupEevee.bl_idname, text=operators.SetupEevee.bl_label, icon='SCENE')
        col.operator(operators.ConvertMaterialsForEevee.bl_idname, text=operators.ConvertMaterialsForEevee.bl_label, icon='NODE_MATERIAL')

        layout.label(text='UI Panels')
        col = layout.column(align=True)
        col.label(text='World > MMD UuuNyaa Lighting Panel', icon='WORLD')
        col.label(text='Material > MMD UuuNyaa Material Panel', icon='MATERIAL')


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
        mmd_uuunyaa_tools_lighting = context.scene.mmd_uuunyaa_tools_lighting

        layout = self.layout
        col = layout.column(align=True)

        # Previews
        row = col.row()
        row.template_icon_view(mmd_uuunyaa_tools_lighting, 'thumbnails', show_labels=True)

        # Lighting Name
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=row.enum_item_name(mmd_uuunyaa_tools_lighting, 'thumbnails', mmd_uuunyaa_tools_lighting.thumbnails))

        lu = lighting_tuner.LightingUtilities(context.scene)
        for obj in bpy.context.view_layer.active_layer_collection.collection.objects.values():
            if obj.type != 'EMPTY' or obj.parent is not None or not lu.object_marker.is_marked(obj):
                continue
            layout.prop(obj, 'location')
            layout.prop(obj, 'scale')
            layout.prop(obj, 'rotation_euler')
            break


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

        mu = material_tuner.MaterialUtilities(material)
        node_frame = mu.find_node_frame()
        if node_frame is not None:
            for node in mu.list_nodes(node_type=bpy.types.ShaderNodeGroup, node_frame=node_frame):
                layout.label(text=node.label)
                for input in node.inputs:
                    if input.is_linked:
                        continue
                    layout.prop(input, 'default_value', text=input.name)

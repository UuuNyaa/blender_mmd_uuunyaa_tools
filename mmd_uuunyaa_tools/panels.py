# -*- coding: utf-8 -*-

import bpy
from mmd_uuunyaa_tools import material_tuner
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

        col = layout.column(align=True)
        col.operator(operators.SetupEevee.bl_idname, text=operators.SetupEevee.bl_label, icon='SCENE')
        col.operator(operators.SetupLights.bl_idname, text=operators.SetupLights.bl_label, icon='LIGHT')
        col.operator(operators.ConvertMaterialsForEevee.bl_idname, text=operators.ConvertMaterialsForEevee.bl_label, icon='NODE_MATERIAL')

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
        material = context.active_object.active_material
        layout = self.layout
        layout.label(text='test')


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
        layout = self.layout
        col = layout.column(align=True)
        mmd_uuunyaa_tools = bpy.context.material.mmd_uuunyaa_tools

        # Previews
        row = col.row()
        row.template_icon_view(mmd_uuunyaa_tools, 'thumbnails', show_labels=True)

        # Material Name
        row = col.row(align=True)
        row.alignment = 'CENTER'
        row.label(text=row.enum_item_name(mmd_uuunyaa_tools, 'thumbnails', mmd_uuunyaa_tools.thumbnails))

        mu = material_tuner.MaterialUtilities(material)
        node_frame = mu.find_node_frame()
        if node_frame is not None:
            for node in mu.list_nodes(node_type=bpy.types.ShaderNodeGroup, node_frame=node_frame):
                layout.label(text=node.label)
                for input in node.inputs:
                    if input.is_linked:
                        continue
                    layout.prop(input, 'default_value', text=input.name)


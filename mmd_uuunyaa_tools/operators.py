# -*- coding: utf-8 -*-

import os
import bpy

import mmd_tools

class ConvertMaterialsForEevee(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.convert_materials_for_eevee'
    bl_label = 'Convert Shaders for Eevee'
    bl_description = 'Convert materials of selected objects for Eevee.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return next((x for x in context.selected_objects if x.type == 'MESH'), None)

    def execute(self, context):
        for obj in (x for x in context.selected_objects if x.type == 'MESH'):
            mmd_tools.cycles_converter.convertToCyclesShader(obj, use_principled=True, clean_nodes=True)

        if context.scene.render.engine != 'BLENDER_EEVEE':
            context.scene.render.engine = 'BLENDER_EEVEE'

        return {'FINISHED'}

PATH_BLENDS_UUUNYAA_LIGHTS = 'blends/UuuNyaa_Lights.blend'

class SetupLights(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.setup_lights_for_eevee'
    bl_label = 'Setup Lights for Eevee'
    bl_description = 'Setup lights for Eevee.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.view_layer.active_layer_collection.collection

    def execute(self, context):
        if 'UuuNyaa Lights' not in bpy.data.collections:
            path = os.path.join(os.path.dirname(__file__), PATH_BLENDS_UUUNYAA_LIGHTS)
            with bpy.data.libraries.load(path, link=False) as (_, data_to):
                data_to.collections = ['UuuNyaa Lights']

        parent = context.view_layer.active_layer_collection.collection.children
        if 'UuuNyaa Lights' not in parent:
            parent.link(bpy.data.collections['UuuNyaa Lights'])

        return {'FINISHED'}

class SetupEevee(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.setup_render_engine_for_eevee'
    bl_label = 'Setup Render Engine for Eevee'
    bl_description = 'Setup render engine properties for Eevee.'
    bl_options = {'REGISTER', 'UNDO'}

    use_bloom: bpy.props.BoolProperty(name='Use Bloom', default=True)
    use_motion_blur: bpy.props.BoolProperty(name='Use Motion Blur', default=False)
    film_transparent: bpy.props.BoolProperty(name='Use Film Transparent', default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        if context.scene.render.engine != 'BLENDER_EEVEE':
            context.scene.render.engine = 'BLENDER_EEVEE'

        eevee = context.scene.eevee

        # Ambient Occlusion: enable
        eevee.use_gtao = True
        # > Distance: 0.1 m
        eevee.gtao_distance = 0.100

        # Bloom: enable
        eevee.use_bloom = self.use_bloom
        if self.use_bloom:
            # > Threshold: 1.000
            eevee.bloom_threshold = 1.000
            # > Intensity: 0.100
            eevee.bloom_intensity = 0.100

        # Depth of Field
        # > Max Size: 16 px
        eevee.bokeh_max_size = 16.000

        # Screen Space Reflections: enable
        eevee.use_ssr = True
        # > Refrection: enable
        eevee.use_ssr_refraction = True
        # > Edge Fading: 0.000
        eevee.ssr_border_fade = 0.000

        # Motion Blur
        eevee.use_motion_blur = self.use_motion_blur

        # Shadows
        # > Cube Size 1024 px
        eevee.shadow_cube_size = '1024'
        # > Cascade Size 2048 px
        eevee.shadow_cascade_size = '2048'

        # Indirect lighting: enable
        # > Irradiance Smoothing: 0.50
        eevee.gi_irradiance_smoothing = 0.50

        # Film > Transparent
        bpy.data.scenes["Scene"].render.film_transparent = self.film_transparent

        # Color Management > Look: High Contrast
        bpy.data.scenes["Scene"].view_settings.look = 'High Contrast'

        return {'FINISHED'}

from mmd_uuunyaa_tools import lighting_tuner
class TuneLighting(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.tune_lighting'
    bl_label = 'Tune Lighting'
    bl_description = 'Tune selected lighting.'
    bl_options = {'REGISTER', 'UNDO'}

    lighting: bpy.props.EnumProperty(
        items=[(id, t.tuner.get_name(), '') for id, t in lighting_tuner.TUNERS.items()],
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        lighting_tuner.TUNERS[self.lighting].tuner(context.scene).execute()
        return {'FINISHED'}

from mmd_uuunyaa_tools import material_tuner
class TuneMaterial(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.tune_material'
    bl_label = 'Tune Material'
    bl_description = 'Tune selected material.'
    bl_options = {'REGISTER', 'UNDO'}

    material: bpy.props.EnumProperty(
        items=[(id, t.tuner.get_name(), '') for id, t in material_tuner.TUNERS.items()],
    )

    @classmethod
    def poll(cls, context):
        return context.object.active_material

    def execute(self, context):
        material_tuner.TUNERS[self.material].tuner(context.object.active_material).execute()
        return {'FINISHED'}

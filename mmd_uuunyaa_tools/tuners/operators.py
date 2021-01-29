
import bpy
from mmd_uuunyaa_tools.tuners import lighting_tuner, material_tuner


class TuneLighting(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.tune_lighting'
    bl_label = 'Tune Lighting'
    bl_description = 'Tune selected lighting.'
    bl_options = {'REGISTER', 'UNDO'}

    lighting: bpy.props.EnumProperty(
        items=lighting_tuner.TUNERS.to_enum_property_items(),
    )

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        lighting_tuner.TUNERS[self.lighting](context.scene).execute()
        return {'FINISHED'}


class TuneMaterial(bpy.types.Operator):
    bl_idname = 'mmd_uuunyaa_tools.tune_material'
    bl_label = 'Tune Material'
    bl_description = 'Tune selected material.'
    bl_options = {'REGISTER', 'UNDO'}

    material: bpy.props.EnumProperty(
        items=material_tuner.TUNERS.to_enum_property_items(),
    )

    @classmethod
    def poll(cls, context):
        return context.object.active_material

    def execute(self, context):
        material_tuner.TUNERS[self.material](context.object.active_material).execute()
        return {'FINISHED'}

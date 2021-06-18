# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import bpy
from mmd_uuunyaa_tools.m17n import _
from mmd_uuunyaa_tools.tuners import lighting_tuners, material_tuners


def update_lighting_thumbnails(prop: 'LightingPropertyGroup', _):
    bpy.ops.mmd_uuunyaa_tools.tune_lighting(lighting=prop.thumbnails)  # pylint: disable=no-member


class LightingPropertyGroup(bpy.types.PropertyGroup):
    thumbnails: bpy.props.EnumProperty(
        items=lighting_tuners.TUNERS.to_enum_property_items(),
        description=_('Choose the lighting you want to use'),
        update=update_lighting_thumbnails,
    )

    @staticmethod
    def register():
        # pylint: disable=assignment-from-no-return
        bpy.types.Collection.mmd_uuunyaa_tools_lighting = bpy.props.PointerProperty(type=LightingPropertyGroup)

    @staticmethod
    def unregister():
        del bpy.types.Collection.mmd_uuunyaa_tools_lighting


def update_material_thumbnails(prop: 'MaterialPropertyGroup', _):
    bpy.ops.mmd_uuunyaa_tools.tune_material(material=prop.thumbnails)  # pylint: disable=no-member


class MaterialPropertyGroup(bpy.types.PropertyGroup):
    thumbnails: bpy.props.EnumProperty(
        items=material_tuners.TUNERS.to_enum_property_items(),
        description=_('Choose the material you want to use'),
        update=update_material_thumbnails,
    )

    @staticmethod
    def register():
        # pylint: disable=assignment-from-no-return
        bpy.types.Material.mmd_uuunyaa_tools_material = bpy.props.PointerProperty(type=MaterialPropertyGroup)

    @staticmethod
    def unregister():
        del bpy.types.Material.mmd_uuunyaa_tools_material

# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import os
from typing import Dict, Any

import bpy
from bpy.types import (
    Material, NodeSocket, NodeFrame,
    ShaderNode, ShaderNodeGroup, ShaderNodeOutputMaterial,
    ShaderNodeBsdfPrincipled, ShaderNodeBsdfGlass, ShaderNodeBsdfTransparent, ShaderNodeMixShader,
    ShaderNodeTexImage, ShaderNodeRGBCurve
)

from mmd_uuunyaa_tools.abstract import TunerABC, TunerRegistry

PATH_BLENDS_UUUNYAA_MATERIALS = 'blends/UuuNyaa_Materials.blend'


class MaterialUtilities:
    def __init__(self, material):
        self.material = material
        self.nodes = material.node_tree.nodes
        self.links = material.node_tree.links

    @staticmethod
    def srgb_to_linearrgb(c: float) -> float:
        if c < 0:
            return 0
        elif c < 0.04045:
            return c/12.92
        else:
            return ((c+0.055)/1.055)**2.4

    @staticmethod
    def hex_to_rgba(hex: int, alpha=1.0) -> (float, float, float, float):
        r = (hex & 0xff0000) >> 16
        g = (hex & 0x00ff00) >> 8
        b = (hex & 0x0000ff)
        return tuple([MaterialUtilities.srgb_to_linearrgb(c/0xff) for c in (r, g, b)] + [alpha])

    @staticmethod
    def to_name(label: str) -> str:
        return label.replace(' ', '_').lower()

    @staticmethod
    def grid_to_position(grid_x: int, grid_y: int) -> (int, int):
        return (grid_x * 300, grid_y * 400)

    def append_node_group(self, name: str):
        if name in bpy.data.node_groups:
            return

        path = os.path.join(os.path.dirname(__file__), PATH_BLENDS_UUUNYAA_MATERIALS)
        with bpy.data.libraries.load(path, link=False) as (_, data_to):
            data_to.node_groups = [name]

    def get_output_node(self) -> ShaderNodeOutputMaterial:
        node_output = next((n for n in self.nodes if isinstance(n, ShaderNodeOutputMaterial) and n.is_active_output), None)
        if node_output is None:
            node_output = self.nodes.new(ShaderNodeOutputMaterial.__name__)
            node_output.is_active_output = True
        return node_output

    def list_nodes(self, node_type: type = None, label: str = None, name: str = None, node_frame: NodeFrame = None):
        for node in self.nodes:
            if ((node_type is None or isinstance(node, node_type))
                    and (label is None or node.label == label)
                    and (name is None or node.name == name)
                    and (node_frame is None or node.parent == node_frame)
                ):
                yield node

    def find_node(self, node_type: type, label: str = None, name: str = None, node_frame: NodeFrame = None) -> ShaderNode:
        return next(self.list_nodes(node_type, label, name, node_frame), None)

    def get_node(self, node_type: type, label: str = None, name: str = None) -> ShaderNode:
        node = self.find_node(node_type, label, name)
        if node is None:
            node = self.nodes.new(node_type.__name__)
            node.label = label if label is not None else ''
            node.name = name if name is not None else self.to_name(label)
        return node

    def get_node_frame(self, label: str = None, name: str = 'uuunyaa_node_frame') -> NodeFrame:
        return self.get_node(NodeFrame, label=label, name=name)

    def find_node_frame(self, label: str = None, name: str = 'uuunyaa_node_frame') -> NodeFrame:
        return self.find_node(NodeFrame, label=label, name=name)

    def get_shader_node(self) -> ShaderNodeBsdfPrincipled:
        return self.get_node(ShaderNodeBsdfPrincipled, label='Principled BSDF')

    def get_glass_bsdf_node(self) -> ShaderNodeBsdfGlass:
        return self.get_node(ShaderNodeBsdfGlass, label='Glass BSDF')

    def get_transparent_bsdf_node(self) -> ShaderNodeBsdfTransparent:
        return self.get_node(ShaderNodeBsdfTransparent, label='Transparent BSDF')

    def get_mix_shader_node(self) -> ShaderNodeMixShader:
        return self.get_node(ShaderNodeMixShader, label='Mix Shader')

    def find_mmd_shader_node(self) -> ShaderNodeGroup:
        return self.find_node(ShaderNodeGroup, name='mmd_shader')

    def find_principled_shader_node(self) -> ShaderNodeBsdfPrincipled:
        return self.find_node(ShaderNodeBsdfPrincipled, label='', name='Principled BSDF')

    def get_base_texture_node(self) -> ShaderNodeTexImage:
        return self.find_node(ShaderNodeTexImage, label='Mmd Base Tex')

    def get_skin_color_adjust_node(self) -> ShaderNodeRGBCurve:
        return self.get_node_group('Skin Color Adjust', label='Skin Color Adjust')

    def get_node_group(self, group_name: str, label: str = None, name: str = None) -> ShaderNodeGroup:
        self.append_node_group(group_name)
        node = self.get_node(ShaderNodeGroup, label, name)
        node.node_tree = bpy.data.node_groups[group_name]
        return node

    def get_skin_bump_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Skin Bump', label='Skin Bump')

    def get_fabric_bump_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Fabric Bump', label='Fabric Bump')

    def get_wave_bump_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Wave Bump', label='Wave Bump')

    def get_shadowless_bsdf_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Shadowless BSDF', label='Shadowless BSDF')

    def get_liquid_bsdf_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Liquid BSDF', label='Liquid BSDF')

    def get_knit_texture_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Knit Texture', label='Knit Texture')

    def get_leather_texture_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Leather Texture', label='Leather Texture')

    def get_tex_uv(self) -> ShaderNodeGroup:
        return self.get_node_group('MMDTexUV', name='mmd_tex_uv')

    def reset(self):
        node_frame = self.find_node_frame()
        if node_frame is None:
            return

        for node in self.list_nodes(node_frame=node_frame):
            self.nodes.remove(node)
        self.nodes.remove(node_frame)

        self.set_material_properties({
            'blend_method': 'HASHED',
            'shadow_method': 'HASHED',
            'use_screen_refraction': False,
            'refraction_depth': 0.000,
        })

    def edit(self, node: ShaderNode, inputs: Dict[str, Any] = {}, properties: Dict[str, Any] = {}, force=False) -> ShaderNode:
        if node is None:
            return None

        self.set_node_inputs(node, inputs, force)
        for name, value in properties.items():
            setattr(node, name, value)
        return node

    def set_material_properties(self, properties: Dict[str, Any] = {}):
        for name, value in properties.items():
            setattr(self.material, name, value)
        return self

    def set_node_inputs(self, node: ShaderNode, values: Dict[str, Any], force=False) -> ShaderNode:
        for key, value in values.items():
            if isinstance(value, NodeSocket):
                if force or not node.inputs[key].is_linked:
                    self.links.new(value, node.inputs[key])
            else:
                node.inputs[key].default_value = value
        return node


class MaterialTunerABC(TunerABC, MaterialUtilities):
    pass


class ResetMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_RESET'

    @classmethod
    def get_name(cls):
        return 'Reset'

    def execute(self):
        self.reset()
        shader_node = self.find_mmd_shader_node()
        if shader_node is None:
            shader_node = self.find_principled_shader_node()

        if shader_node is None:
            return

        self.edit(self.get_output_node(), {
            'Surface': shader_node.outputs[0],
        }, force=True)


class TransparentMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_TRANSPARENT'

    @classmethod
    def get_name(cls):
        return 'Transparent'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_transparent_bsdf_node(), properties={'location': self.grid_to_position(-1, -0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)

        self.set_material_properties({
            'blend_method': 'HASHED',
            'shadow_method': 'HASHED',
            'use_screen_refraction': True,
            'refraction_depth': 0.000,
        })


class EyeHighlightMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_EYE_HIGHLIGHT'

    @classmethod
    def get_name(cls):
        return 'Eye Highlight'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shadowless_bsdf_node(), {
                'Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0xFFFFFF),
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
                'Emission': self.hex_to_rgba(0x999999),
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)

        self.edit(self.get_tex_uv(), properties={'location': self.grid_to_position(-3, +0)})


class EyeWhiteMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_EYE_WHITE'

    @classmethod
    def get_name(cls):
        return 'Eye White'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shadowless_bsdf_node(), {
                'Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0xFFFFFF),
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
                'Emission': self.hex_to_rgba(0x666666),
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)

        self.edit(self.get_tex_uv(), properties={'location': self.grid_to_position(-3, +0)})


class EyeIrisMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_EYE_IRIS'

    @classmethod
    def get_name(cls):
        return 'Eye Iris'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0x00001E),
                'Specular': 0.000,
                'Roughness': 0.500,
                'Clearcoat': 1.000,
                'Clearcoat Roughness': 0.030,
                'IOR': 1.450,
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class EyeLashMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_EYE_LASH'

    @classmethod
    def get_name(cls):
        return 'Eye Lash'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0x122837),
                'Specular': 0.000,
                'Roughness': 1.000,
                'IOR': 1.450,
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class HairMatteMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_HAIR_MATTE'

    @classmethod
    def get_name(cls):
        return 'Hair Matte'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0x698E9A),
                'Specular': 0.200,
                'Roughness': 0.600,
                'IOR': 1.450,
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class SkinMucosaMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_SKIN_MUCOSA'

    @classmethod
    def get_name(cls):
        return 'Skin Mucosa'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})


        node_skin_bump = self.edit(self.get_skin_bump_node(), {
            'Vector': self.edit(self.get_tex_uv(), properties={'location': self.grid_to_position(-3, +0)}).outputs['Base UV'],
            'Scale': 1.000,
            'Strength': 1.000,
        }, {'location': self.grid_to_position(-1, -1), 'parent': node_frame})

        node_skin_color_adjust = self.edit(self.get_skin_color_adjust_node(), {
            'Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0xEEAA99),
            'Blood Color': self.hex_to_rgba(0xE40000),
        }, {'location': self.grid_to_position(-1, +0), 'parent': node_frame})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': node_skin_color_adjust.outputs['Color'],
                'Subsurface': 0.200,
                'Subsurface Color': node_skin_color_adjust.outputs['Blood Color'],
                'Specular': 0.300,
                'Roughness': 0.200,
                'Clearcoat': 1.000,
                'Clearcoat Roughness': 0.030,
                'IOR': 1.450,
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
                'Normal': node_skin_bump.outputs['Normal'],
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class SkinBumpMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_SKIN_BUMP'

    @classmethod
    def get_name(cls):
        return 'Skin Bump'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})

        node_skin_bump = self.edit(self.get_skin_bump_node(), {
            'Vector': self.edit(self.get_tex_uv(), properties={'location': self.grid_to_position(-3, +0)}).outputs['Base UV'],
            'Scale': 1.000,
            'Strength': 1.000,
        }, {'location': self.grid_to_position(-1, -1), 'parent': node_frame})

        node_skin_color_adjust = self.edit(self.get_skin_color_adjust_node(), {
            'Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0xEEAA99),
            'Blood Color': self.hex_to_rgba(0xE40000),
        }, {'location': self.grid_to_position(-1, +0), 'parent': node_frame})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': node_skin_color_adjust.outputs['Color'],
                'Subsurface': 0.044,
                'Subsurface Color': node_skin_color_adjust.outputs['Blood Color'],
                'Specular': 0.200,
                'Roughness': 0.550,
                'IOR': 1.450,
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
                'Normal': node_skin_bump.outputs['Normal'],
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class FabricBumpMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_FABRIC_BUMP'

    @classmethod
    def get_name(cls):
        return 'Fabric Bump'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0x999999),
                'Specular': 0.130,
                'Roughness': 1.000,
                'IOR': 1.450,
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
                'Normal': self.edit(self.get_fabric_bump_node(), {
                    'Vector': self.edit(self.get_tex_uv(), properties={'location': self.grid_to_position(-3, +0)}).outputs['Base UV'],
                    'Scale': 1.000,
                    'Strength': 1.000,
                }, {'location': self.grid_to_position(-1, -1), 'parent': node_frame}).outputs['Normal'],
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class FabricWaveMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_FABRIC_WAVE'

    @classmethod
    def get_name(cls):
        return 'Fabric Wave'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0x999999),
                'Specular': 0.130,
                'Roughness': 1.000,
                'IOR': 1.450,
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
                'Normal': self.edit(self.get_wave_bump_node(), {
                    'Vector': self.edit(self.get_tex_uv(), properties={'location': self.grid_to_position(-3, +0)}).outputs['Base UV'],
                    'Scale': 100.000,
                    'Angle': 0.000,
                    'Fac': 0.500,
                    'Strength': 1.000,
                }, {'location': self.grid_to_position(-1, -1), 'parent': node_frame}).outputs['Normal'],
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class FabricKnitMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_FABRIC_KNIT'

    @classmethod
    def get_name(cls):
        return 'Fabric Knit'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})
        knit_texture = self.edit(self.get_knit_texture_node(), {
            'Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0xFFBAAE),
            'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
            'Hole Alpha': 0.000,
            'Vector': self.edit(self.get_tex_uv(), properties={'location': self.grid_to_position(-3, +0)}).outputs['Base UV'],
            'Random Hue': 0.500,
            'Scale': 30.000,
            'X Compression': 1.500,
        }, {'location': self.grid_to_position(-1, +0), 'parent': node_frame})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': knit_texture.outputs['Color'],
                'Specular': 0.200,
                'Roughness': 0.800,
                'IOR': 1.450,
                'Alpha': knit_texture.outputs['Alpha'],
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
            'Displacement': knit_texture.outputs['Displacement'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class FabricLeatherMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_FABRIC_LEATHER'

    @classmethod
    def get_name(cls):
        return 'Fabric Leather'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})
        leather_texture = self.edit(self.get_leather_texture_node(), {
            'Primary Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0x000000),
            'Secondary Color': self.hex_to_rgba(0x333333),
            'Roughness': 0.450,
            'Old/New': 4.000,
            'Scale': 100.000,
            'Strength': 0.150,
            'Tartiary Detail': 2.000,
            'Vector': self.edit(self.get_tex_uv(), properties={'location': self.grid_to_position(-3, +0)}).outputs['Base UV'],
        }, {'location': self.grid_to_position(-1, +0), 'parent': node_frame})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': leather_texture.outputs['Color'],
                'Specular': 0.200,
                'Roughness': leather_texture.outputs['Roughness'],
                'Sheen': 0.300,
                'IOR': 1.450,
                'Alpha': 1.000,
                'Normal': leather_texture.outputs['Normal'],
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class PlasticGlossMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_PLASTIC_GLOSS'

    @classmethod
    def get_name(cls):
        return 'Plastic Gloss'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0x666666),
                'Specular': 0.500,
                'Roughness': 0.700,
                'Clearcoat': 0.200,
                'IOR': 1.450,
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class PlasticEmissionMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_PLASTIC_EMISSION'

    @classmethod
    def get_name(cls):
        return 'Plastic Emission'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())
        node_base_texture = self.edit(self.get_base_texture_node(), properties={'location': self.grid_to_position(-2, +0)})

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_shader_node(), {
                'Base Color': self.hex_to_rgba(0x000000),
                'Specular': 0.500,
                'Roughness': 0.700,
                'Clearcoat': 0.200,
                'IOR': 1.450,
                'Emission': node_base_texture.outputs['Color'] if node_base_texture else self.hex_to_rgba(0xFF6666),
                'Alpha': node_base_texture.outputs['Alpha'] if node_base_texture else 1.000,
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)


class LiquidWaterMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_LIQUID_WATER'

    @classmethod
    def get_name(cls):
        return 'Liquid Water'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_liquid_bsdf_node(), {
                'Roughness': 0.000,
                'IOR': 1.333,
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['BSDF'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)

        self.set_material_properties({
            'blend_method': 'HASHED',
            'shadow_method': 'HASHED',
            'use_screen_refraction': True,
            'refraction_depth': 0.000,
        })


class LiquidCloudyMaterialTuner(MaterialTunerABC):
    @classmethod
    def get_id(cls):
        return 'MATERIAL_LIQUID_CLOUDY'

    @classmethod
    def get_name(cls):
        return 'Liquid Cloudy'

    def execute(self):
        self.reset()
        node_frame = self.get_node_frame(self.get_name())

        self.edit(self.get_output_node(), {
            'Surface': self.edit(self.get_mix_shader_node(), {
                'Fac': 0.300,
                1: self.edit(self.get_liquid_bsdf_node(), {
                    'Roughness': 0.000,
                    'IOR': 1.333,
                }, {'location': self.grid_to_position(-1, +0), 'parent': node_frame}).outputs['BSDF'],
                2: self.edit(self.get_shader_node(), {
                    'Base Color': self.hex_to_rgba(0xE7E7E7),
                    'Specular': 1.000,
                    'Roughness': 0.000,
                    'Clearcoat': 1.000,
                    'IOR': 1.450,
                }, {'location': self.grid_to_position(-1, -1), 'parent': node_frame}).outputs['BSDF'],
            }, {'location': self.grid_to_position(+0, +0), 'parent': node_frame}).outputs['Shader'],
        }, {'location': self.grid_to_position(+1, +0)}, force=True)

        self.set_material_properties({
            'blend_method': 'HASHED',
            'shadow_method': 'HASHED',
            'use_screen_refraction': True,
            'refraction_depth': 0.000,
        })


TUNERS = TunerRegistry(
    ResetMaterialTuner,
    TransparentMaterialTuner,
    EyeHighlightMaterialTuner,
    EyeWhiteMaterialTuner,
    EyeIrisMaterialTuner,
    EyeLashMaterialTuner,
    HairMatteMaterialTuner,
    SkinMucosaMaterialTuner,
    SkinBumpMaterialTuner,
    FabricBumpMaterialTuner,
    FabricWaveMaterialTuner,
    FabricKnitMaterialTuner,
    FabricLeatherMaterialTuner,
    PlasticGlossMaterialTuner,
    PlasticEmissionMaterialTuner,
    LiquidWaterMaterialTuner,
    LiquidCloudyMaterialTuner,
)

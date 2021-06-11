# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import os
from typing import Any, Dict, Iterable, Tuple, Union

import bpy
from bpy.types import (NodeFrame, NodeSocket, ShaderNode, ShaderNodeBsdfGlass,
                       ShaderNodeBsdfPrincipled, ShaderNodeBsdfTransparent,
                       ShaderNodeBump, ShaderNodeGroup, ShaderNodeMath,
                       ShaderNodeMixShader, ShaderNodeOutputMaterial,
                       ShaderNodeRGBCurve, ShaderNodeTexImage, ShaderNodeValue,
                       ShaderNodeVertexColor)
from mmd_uuunyaa_tools import PACKAGE_PATH

PATH_BLENDS_UUUNYAA_MATERIALS = os.path.join(PACKAGE_PATH, 'blends', 'UuuNyaa_Materials.blend')


class NodeUtilities:
    def __init__(self, node_tree: bpy.types.NodeTree) -> None:
        super().__init__()
        self.node_tree = node_tree
        self.nodes = node_tree.nodes
        self.links = node_tree.links

    @staticmethod
    def srgb_to_linearrgb(color: float) -> float:
        if color < 0:
            return 0
        if color < 0.04045:
            return color/12.92
        return ((color+0.055)/1.055)**2.4

    @staticmethod
    def hex_to_rgba(hex_int: int, alpha=1.0) -> Tuple[float, float, float, float]:
        # pylint: disable=invalid-name
        # r,g,b is commonly used
        r = (hex_int & 0xff0000) >> 16
        g = (hex_int & 0x00ff00) >> 8
        b = (hex_int & 0x0000ff)
        return tuple([NodeUtilities.srgb_to_linearrgb(c/0xff) for c in (r, g, b)] + [alpha])

    @staticmethod
    def to_name(label: str) -> str:
        return label.replace(' ', '_').lower()

    @staticmethod
    def append_node_group(name: str):
        if name in bpy.data.node_groups:
            return

        with bpy.data.libraries.load(PATH_BLENDS_UUUNYAA_MATERIALS, link=False) as (_, data_to):
            data_to.node_groups = [name]

    @staticmethod
    def grid_to_position(grid_x: int, grid_y: int) -> Tuple[int, int]:
        return (grid_x * 100, grid_y * 100)

    def get_output_node(self) -> ShaderNodeOutputMaterial:
        node_output = next((n for n in self.nodes if isinstance(n, ShaderNodeOutputMaterial) and n.is_active_output), None)
        if node_output is None:
            node_output = self.nodes.new(ShaderNodeOutputMaterial.__name__)
            node_output.is_active_output = True
        return node_output

    def list_nodes(self, node_type: type = None, label: str = None, name: str = None, node_frame: NodeFrame = None) -> Iterable[ShaderNode]:
        for node in self.nodes:
            if node_type is not None and not isinstance(node, node_type):
                continue

            if label is not None and node.label != label:
                continue

            if name is not None and node.name != name:
                continue

            if node_frame is not None and node.parent != node_frame:
                continue

            yield node

    @staticmethod
    def check_setting_node(node: ShaderNode) -> bool:
        return node.label

    @staticmethod
    def check_adjuster_node(node: ShaderNode) -> bool:
        return isinstance(node, ShaderNodeGroup) and node.label.endswith(' Adjuster')

    @staticmethod
    def to_link_or_value(node_socket: bpy.types.NodeSocket):
        if not node_socket.is_linked:
            return node_socket.default_value

        return node_socket.links[0].from_socket

    def find_node(self, node_type: type, label: str = None, name: str = None, node_frame: NodeFrame = None) -> ShaderNode:
        return next(self.list_nodes(node_type, label, name, node_frame), None)

    def new_node(self, node_type: type, label: str = None, name: str = None) -> ShaderNode:
        node = self.nodes.new(node_type.__name__)
        node.label = label if label is not None else ''
        node.name = name if name is not None else self.to_name(label)
        return node

    def get_node(self, node_type: type, label: str = None, name: str = None) -> ShaderNode:
        node = self.find_node(node_type, label, name)
        if node is not None:
            return node

        return self.new_node(node_type, label, name)

    def get_node_frame(self, label: str = None, name: str = 'uuunyaa_node_frame') -> NodeFrame:
        return self.get_node(NodeFrame, label=label, name=name)

    def find_node_frame(self, label: str = None, name: str = 'uuunyaa_node_frame') -> NodeFrame:
        return self.find_node(NodeFrame, label=label, name=name)

    def remove_node_frame(self, node_frame: NodeFrame):
        for node in self.list_nodes(node_frame=node_frame):
            self.nodes.remove(node)
        self.nodes.remove(node_frame)

    def get_node_group(self, group_name: str, label: str = None, name: str = None) -> ShaderNodeGroup:
        self.append_node_group(group_name)
        node = self.get_node(ShaderNodeGroup, label, name)
        node.node_tree = bpy.data.node_groups[group_name]
        return node

    def edit(self, node: ShaderNode, inputs: Dict[str, Any] = {}, properties: Dict[str, Any] = {}, force=False) -> ShaderNode:
        # pylint: disable=dangerous-default-value
        # because readonly
        if node is None:
            return None

        self.set_node_inputs(node, inputs, force)
        for name, value in properties.items():
            setattr(node, name, value)
        return node

    def set_node_inputs(self, node: ShaderNode, values: Dict[str, Any], force=False) -> ShaderNode:
        for key, value in values.items():
            if isinstance(value, NodeSocket):
                if force or not node.inputs[key].is_linked:
                    self.links.new(value, node.inputs[key])
            else:
                node.inputs[key].default_value = value
        return node

    def draw_setting_node_properties(self, layout: bpy.types.UILayout, nodes: Iterable[ShaderNode]):
        for node in nodes:
            if isinstance(node, ShaderNodeGroup):
                pass
            elif self.check_setting_node(node):
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


class MaterialUtilities(NodeUtilities):
    # pylint: disable=too-many-public-methods

    def __init__(self, material: bpy.types.Material):
        super().__init__(material.node_tree)
        self.material = material

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

    def find_active_principled_shader_node(self) -> Union[ShaderNodeBsdfPrincipled, None]:
        node_output = self.get_output_node()
        node_from = node_output.inputs['Surface'].links[0].from_node

        if isinstance(node_from, ShaderNodeBsdfPrincipled):
            return node_from

        return None

    def new_bump_node(self) -> ShaderNodeBump:
        return self.new_node(ShaderNodeBump, label='Bump')

    def new_math_node(self) -> ShaderNodeMath:
        return self.new_node(ShaderNodeMath, label='Math')

    def get_vertex_color_node(self) -> ShaderNodeVertexColor:
        return self.get_node(ShaderNodeVertexColor, label='Vertex Color')

    def get_base_texture_node(self) -> ShaderNodeTexImage:
        return self.find_node(ShaderNodeTexImage, label='Mmd Base Tex')

    def get_skin_color_adjust_node(self) -> ShaderNodeRGBCurve:
        return self.get_node_group('Skin Color Adjust', label='Skin Color Adjust')

    def get_skin_bump_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Skin Bump', label='Skin Bump')

    def get_fabric_woven_texture_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Fabric Woven Texture', label='Fabric Woven Texture')

    def get_fabric_bump_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Fabric Bump', label='Fabric Bump')

    def get_wave_bump_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Wave Bump', label='Wave Bump')

    def get_magic_bump_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Magic Bump', label='Magic Bump')

    def get_shadowless_bsdf_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Shadowless BSDF', label='Shadowless BSDF')

    def get_gem_bsdf_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Gem BSDF', label='Gem BSDF')

    def get_liquid_bsdf_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Liquid BSDF', label='Liquid BSDF')

    def get_knit_texture_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Knit Texture', label='Knit Texture')

    def get_leather_texture_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Leather Texture', label='Leather Texture')

    def get_tex_uv(self) -> ShaderNodeGroup:
        return self.get_node_group('MMDTexUV', name='mmd_tex_uv')

    def get_subsurface_adjuster_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Subsurface Adjuster', label='Subsurface Adjuster')

    def get_wet_adjuster_node(self) -> ShaderNodeGroup:
        return self.get_node_group('Wet Adjuster', label='Wet Adjuster')

    _adjusters_node_frame_label = 'UuuNyaa Adjusters'
    _adjusters_node_frame_name = 'uuunyaa_adjusters_node_frame'

    def find_adjusters_node_frame(self) -> NodeFrame:
        return self.find_node_frame(label=self._adjusters_node_frame_label, name=self._adjusters_node_frame_name)

    def get_adjusters_node_frame(self) -> NodeFrame:
        return self.get_node_frame(label=self._adjusters_node_frame_label, name=self._adjusters_node_frame_name)

    def reset(self):
        node_frame = self.find_adjusters_node_frame()
        if node_frame is not None:
            self.remove_node_frame(node_frame)

        node_frame = self.find_node_frame()
        if node_frame is None:
            return

        self.remove_node_frame(node_frame)

        self.set_material_properties({
            'blend_method': 'HASHED',
            'shadow_method': 'HASHED',
            'use_screen_refraction': False,
            'refraction_depth': 0.000,
        })

    def set_material_properties(self, properties: Dict[str, Any] = {}):
        # pylint: disable=dangerous-default-value
        # because readonly
        for name, value in properties.items():
            setattr(self.material, name, value)
        return self

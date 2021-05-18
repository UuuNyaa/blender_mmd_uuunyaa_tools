# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import os
from typing import Any, Dict, Iterable, Tuple

import bpy
from bpy.types import (NodeFrame, NodeSocket, ShaderNode, ShaderNodeGroup,
                       ShaderNodeOutputMaterial)
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
    def is_setting_node(node: ShaderNode) -> bool:
        return node.label

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

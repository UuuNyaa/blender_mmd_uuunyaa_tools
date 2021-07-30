# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from abc import abstractmethod

from bpy.types import NodeFrame, ShaderNodeGroup
from mmd_uuunyaa_tools.editors import MaterialEditor
from mmd_uuunyaa_tools.m17n import _


class MaterialAdjusterUtilities(MaterialEditor):

    def check_attached(self, label: str) -> bool:
        return self.find_node(ShaderNodeGroup, label=label) is not None

    def check_attachable(self) -> bool:
        return self.find_active_principled_shader_node() is not None

    def clean_adjusters_node_frame(self) -> NodeFrame:
        node_frame = self.get_adjusters_node_frame()

        if next(self.list_nodes(node_frame=node_frame), None) is not None:
            return

        self.nodes.remove(node_frame)


class MaterialAdjusterABC(MaterialAdjusterUtilities):
    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        pass

    @abstractmethod
    def attach(self) -> ShaderNodeGroup:
        pass

    @abstractmethod
    def detach(self):
        pass

    def detach_and_clean(self):
        self.detach()
        self.clean_adjusters_node_frame()

    def is_attached(self) -> bool:
        return self.check_attached(self.get_name())


class WetAdjuster(MaterialAdjusterABC):
    @classmethod
    def get_id(cls) -> str:
        return 'MATERIAL_ADJUSTER_WET'

    @classmethod
    def get_name(cls) -> str:
        return _('Wet Adjuster')

    translation_properties = [
        _('Specular'),
        _('Roughness'),
        _('Wet'),
    ]

    def attach(self):
        node_frame = self.get_adjusters_node_frame()
        node_wet_adjuster = self.find_node(ShaderNodeGroup, label=WetAdjuster.get_name(), node_frame=node_frame)

        node_shader = self.find_active_principled_shader_node()
        node_wet_adjuster = self.edit(self.get_wet_adjuster_node(), {
            'Specular': self.to_link_or_value(node_shader.inputs['Specular']),
            'Roughness': self.to_link_or_value(node_shader.inputs['Roughness']),
            'Wet': self.edit(self.get_vertex_color_node(), {}, {'location': self.grid_to_position(-4, -10), 'parent': node_frame}).outputs['Color'],
        }, {'location': self.grid_to_position(-2, -10), 'parent': node_frame})

        self.edit(node_shader, {
            'Specular': node_wet_adjuster.outputs['Specular'],
            'Roughness': node_wet_adjuster.outputs['Roughness'],
        }, force=True)

        return node_wet_adjuster

    def detach(self):
        node_wet_adjuster = self.get_wet_adjuster_node()

        self.edit(self.find_active_principled_shader_node(), {
            'Specular': self.to_link_or_value(node_wet_adjuster.inputs['Specular']),
            'Roughness': self.to_link_or_value(node_wet_adjuster.inputs['Roughness']),
        }, force=True)

        self.nodes.remove(node_wet_adjuster)
        self.nodes.remove(self.get_vertex_color_node())


class SubsurfaceAdjuster(MaterialAdjusterABC):
    @classmethod
    def get_id(cls) -> str:
        return 'MATERIAL_ADJUSTER_SUBSURFACE'

    @classmethod
    def get_name(cls) -> str:
        return _('Subsurface Adjuster')

    translation_properties = [
        _('Min'),
        _('Max'),
        _('Blood Color'),
        _('Subsurface'),
        _('Subsurface Color'),
    ]

    def attach(self) -> ShaderNodeGroup:
        node_frame = self.get_adjusters_node_frame()
        node_subsurface_adjuster = self.find_node(ShaderNodeGroup, label=self.get_name(), node_frame=node_frame)

        node_shader = self.find_active_principled_shader_node()
        node_subsurface_adjuster = self.edit(self.get_subsurface_adjuster_node(), {
            'Min': self.to_link_or_value(node_shader.inputs['Subsurface']),
            'Max': 0.300,
            'Blood Color': self.to_link_or_value(node_shader.inputs['Subsurface Color']),
        }, {'location': self.grid_to_position(-2, -8), 'parent': node_frame})

        self.edit(node_shader, {
            'Subsurface':  node_subsurface_adjuster.outputs['Subsurface'],
            'Subsurface Color': node_subsurface_adjuster.outputs['Subsurface Color'],
        }, force=True)

        return node_subsurface_adjuster

    def detach(self):
        node_subsurface_adjuster = self.get_subsurface_adjuster_node()

        self.edit(self.find_active_principled_shader_node(), {
            'Subsurface': self.to_link_or_value(node_subsurface_adjuster.inputs['Min']),
            'Subsurface Color': self.to_link_or_value(node_subsurface_adjuster.inputs['Blood Color']),
        }, force=True)

        self.nodes.remove(node_subsurface_adjuster)


ADJUSTERS = {
    WetAdjuster.get_name(): WetAdjuster,
    SubsurfaceAdjuster.get_name(): SubsurfaceAdjuster,
}

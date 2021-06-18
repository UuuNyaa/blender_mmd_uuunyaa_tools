# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import os
from typing import Union

from bpy.types import Object
from mmd_uuunyaa_tools import PACKAGE_PATH
from mmd_uuunyaa_tools.m17n import _
from mmd_uuunyaa_tools.tuners import TunerABC, TunerRegistry
from mmd_uuunyaa_tools.utilities import ObjectAppender, ObjectMarker

PATH_BLENDS_UUUNYAA_LIGHTINGS = os.path.join(PACKAGE_PATH, 'blends', 'UuuNyaa_Lightings.blend')


class LightingUtilities:
    def __init__(self, collection):
        self.collection = collection
        self.object_appender = ObjectAppender(
            'mmd_uuunyaa_tools_lighting_mark',
            PATH_BLENDS_UUUNYAA_LIGHTINGS
        )

    @property
    def object_marker(self) -> ObjectMarker:
        return self.object_appender

    def find_active_lighting(self) -> Union[Object, None]:
        for obj in self.collection.objects.values():
            if obj.type != 'EMPTY' or obj.parent is not None or not self.object_marker.is_marked(obj):
                continue
            return obj

        return None


class LightingTunerABC(TunerABC, LightingUtilities):
    def reset(self):
        self.object_appender.remove_objects(self.collection)

    def add_lights(self, name: str):
        self.object_appender.append_objects_from_collection(name, self.collection)


class ResetLightingTuner(LightingTunerABC):
    @classmethod
    def get_id(cls) -> str:
        return 'LIGHTING_RESET'

    @classmethod
    def get_name(cls) -> str:
        return _('Reset')

    def execute(self):
        self.reset()


class LeftAccentLightingTuner(LightingTunerABC):
    @classmethod
    def get_id(cls) -> str:
        return 'LIGHTING_LEFT_ACCENT'

    @classmethod
    def get_name(cls) -> str:
        return _('Left Accent')

    def execute(self):
        self.reset()
        self.add_lights(self.get_id())


class DoubleSideAccentLightingTuner(LightingTunerABC):
    @classmethod
    def get_id(cls) -> str:
        return 'LIGHTING_DOUBLE_SIDE_ACCENT'

    @classmethod
    def get_name(cls) -> str:
        return _('Double Side Accent')

    def execute(self):
        self.reset()
        self.add_lights(self.get_id())


class GodRayLightingTuner(LightingTunerABC):
    @classmethod
    def get_id(cls) -> str:
        return 'LIGHTING_GOD_RAY'

    @classmethod
    def get_name(cls) -> str:
        return _('God Ray')

    def execute(self):
        self.reset()
        self.add_lights(self.get_id())


class BacklightLightingTuner(LightingTunerABC):
    @classmethod
    def get_id(cls) -> str:
        return 'LIGHTING_BACKLIGHT'

    @classmethod
    def get_name(cls) -> str:
        return _('Backlight')

    def execute(self):
        self.reset()
        self.add_lights(self.get_id())


class LightProbeGridLightingTuner(LightingTunerABC):
    @classmethod
    def get_id(cls) -> str:
        return 'LIGHTING_LIGHT_PROBE_GRID'

    @classmethod
    def get_name(cls) -> str:
        return _('Light Probe Grid')

    def execute(self):
        self.reset()
        self.add_lights(self.get_id())


TUNERS = TunerRegistry(
    (0, ResetLightingTuner),
    (1, LeftAccentLightingTuner),
    (5, DoubleSideAccentLightingTuner),
    (2, GodRayLightingTuner),
    (3, BacklightLightingTuner),
    (4, LightProbeGridLightingTuner),
)

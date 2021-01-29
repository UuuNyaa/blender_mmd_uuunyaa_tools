# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import os
from typing import Any, Dict

import bpy
from mmd_uuunyaa_tools import PACKAGE_PATH
from mmd_uuunyaa_tools.tuners import TunerABC, TunerRegistry
from mmd_uuunyaa_tools.utilities import ObjectAppender, ObjectMarker

PATH_BLENDS_UUUNYAA_LIGHTINGS = os.path.join(PACKAGE_PATH, 'blends', 'UuuNyaa_Lightings.blend')


class LightingUtilities:
    def __init__(self, scene):
        self.scene = scene
        self.object_appender = ObjectAppender(
            'mmd_uuunyaa_tools_lighting',
            PATH_BLENDS_UUUNYAA_LIGHTINGS
        )

    @property
    def object_marker(self) -> ObjectMarker:
        return self.object_appender


class LightingTunerABC(TunerABC, LightingUtilities):
    def reset(self):
        self.object_appender.remove_objects()

    def add_lights(self, name: str):
        self.object_appender.append_objects_from_collection(name)


class ResetLightingTuner(LightingTunerABC):
    @classmethod
    def get_id(cls):
        return 'LIGHTING_RESET'

    @classmethod
    def get_name(cls):
        return 'Reset'

    def execute(self):
        self.reset()


class LeftAccentLightingTuner(LightingTunerABC):
    @classmethod
    def get_id(cls):
        return 'LIGHTING_LEFT_ACCENT'

    @classmethod
    def get_name(cls):
        return 'Left Accent'

    def execute(self):
        self.reset()
        self.add_lights(self.get_id())


class GodRayLightingTuner(LightingTunerABC):
    @classmethod
    def get_id(cls):
        return 'LIGHTING_GOD_RAY'

    @classmethod
    def get_name(cls):
        return 'God Ray'

    def execute(self):
        self.reset()
        self.add_lights(self.get_id())


class BacklightLightingTuner(LightingTunerABC):
    @classmethod
    def get_id(cls):
        return 'LIGHTING_BACKLIGHT'

    @classmethod
    def get_name(cls):
        return 'Backlight'

    def execute(self):
        self.reset()
        self.add_lights(self.get_id())


TUNERS = TunerRegistry(
    ResetLightingTuner,
    LeftAccentLightingTuner,
    GodRayLightingTuner,
    BacklightLightingTuner,
)

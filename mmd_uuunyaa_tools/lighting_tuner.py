# -*- coding: utf-8 -*-

import os
from typing import Dict, Any

import bpy

from mmd_uuunyaa_tools.abstract import TunerABC, TunerDescription

PATH_BLENDS_UUUNYAA_LIGHTINGS = 'blends/UuuNyaa_Lightings.blend'

class LightingUtilities:
    def __init__(self, scene):
        self.scene = scene

    def reset(self):
        pass

class LightingTunerABC(TunerABC, LightingUtilities):
    pass

class ResetLightingTuner(LightingTunerABC):
    @classmethod
    def get_name(cls):
        return 'Reset'

    def execute(self):
        self.reset()

class LeftAccentLightingTuner(LightingTunerABC):
    @classmethod
    def get_name(cls):
        return 'Left Accent'

    def execute(self):
        self.reset()

class BacklightLightingTuner(LightingTunerABC):
    @classmethod
    def get_name(cls):
        return 'Backlight'

    def execute(self):
        self.reset()

TUNERS: Dict[str, TunerDescription] = {
    'LIGHTING_RESET':       TunerDescription(ResetLightingTuner,      'LIGHTING_RESET.png'       ),
    'LIGHTING_LEFT_ACCENT': TunerDescription(LeftAccentLightingTuner, 'LIGHTING_LEFT_ACCENT.png' ),
    'LIGHTING_BACKLIGHT':   TunerDescription(BacklightLightingTuner,  'LIGHTING_BACKLIGHT.png'   ),
}
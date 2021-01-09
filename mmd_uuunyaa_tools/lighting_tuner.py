# -*- coding: utf-8 -*-
# (C) 2021 UuuNyaa <UuuNyaa@gmail.com>

import os
from typing import Dict, Any

import bpy

from mmd_uuunyaa_tools.abstract import TunerABC, TunerDescription
from mmd_uuunyaa_tools.utilities import ObjectAppender

PATH_BLENDS_UUUNYAA_LIGHTINGS = 'blends/UuuNyaa_Lightings.blend'

class LightingTunerABC(TunerABC, ObjectAppender):
    def __init__(self):
        self.object_appender = ObjectAppender(
            'mmd_uuunyaa_tools_lighting',
            os.path.join(os.path.dirname(__file__), PATH_BLENDS_UUUNYAA_LIGHTINGS)
        )
    
    def reset(self):
        self.object_appender.remove_objects()

    def add_lights(self, name: str):
        self.object_appender.append_objects_from_collection(name)

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
        self.add_lights(self.get_name())
    
class BacklightLightingTuner(LightingTunerABC):
    @classmethod
    def get_name(cls):
        return 'Backlight'

    def execute(self):
        self.reset()
        self.add_lights(self.get_name())

TUNERS: Dict[str, TunerDescription] = {
    'LIGHTING_RESET':       TunerDescription(ResetLightingTuner,      'LIGHTING_RESET.png'       ),
    'LIGHTING_LEFT_ACCENT': TunerDescription(LeftAccentLightingTuner, 'LIGHTING_LEFT_ACCENT.png' ),
    'LIGHTING_BACKLIGHT':   TunerDescription(BacklightLightingTuner,  'LIGHTING_BACKLIGHT.png'   ),
}
# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import os
from abc import ABC, abstractmethod
from typing import Dict, NamedTuple

import bpy
import bpy.utils.previews
from mmd_uuunyaa_tools import PACKAGE_PATH


class TunerABC(ABC):
    @classmethod
    @abstractmethod
    def get_id(cls):
        pass

    @classmethod
    @abstractmethod
    def get_name(cls):
        pass

    @abstractmethod
    def execute(self):
        pass


class TunerDescription(NamedTuple):
    tuner: type
    icon_filename: str
    icon_id: int


class TunerRegistry:
    def __init__(self, *tuners: TunerABC):
        self.previews = bpy.utils.previews.new()

        self.tuners: Dict[str, TunerDescription] = {}
        for t in tuners:
            self.add(t)

    def __del__(self):
        del self.previews

    def __getitem__(self, tuner_id: str) -> TunerABC:
        return self.tuners[tuner_id].tuner

    def add(self, tuner: TunerABC, icon_filename: str = None):
        if icon_filename is None:
            icon_filename = tuner.get_id() + '.png'

        icon_path = os.path.join(PACKAGE_PATH, 'thumbnails', icon_filename)
        icon_id = self.previews.load(icon_filename, icon_path, 'IMAGE').icon_id
        self.tuners[tuner.get_id()] = TunerDescription(tuner, icon_filename, icon_id)

    def to_enum_property_items(self):
        return [(id, t.tuner.get_name(), '', t.icon_id, i) for i, (id, t) in enumerate(self.tuners.items())]

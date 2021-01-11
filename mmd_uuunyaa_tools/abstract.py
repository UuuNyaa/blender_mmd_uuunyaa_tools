# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from abc import ABC, abstractmethod
from typing import NamedTuple, Dict


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


class TunerRegistry():
    def __init__(self, *tuners: TunerABC):
        self.tuners: Dict[str, TunerDescription] = {}
        for t in tuners:
            self.add(t)

    def __getitem__(self, tuner_id: str) -> TunerABC:
        return self.tuners[tuner_id].tuner

    def add(self, tuner: TunerABC, icon_filename: str = None):
        self.tuners[tuner.get_id()] = TunerDescription(tuner, icon_filename if icon_filename is not None else tuner.get_id() + '.png')

    def to_enum_property_items(self, previews=None):
        if previews is None:
            return [(id, t.tuner.get_name(), '') for id, t in self.tuners.items()]
        else:
            return [(id, t.tuner.get_name(), '', previews[t.icon_filename].icon_id, i) for i, (id, t) in enumerate(self.tuners.items())]

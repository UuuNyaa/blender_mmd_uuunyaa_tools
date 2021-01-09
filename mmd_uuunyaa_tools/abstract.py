# -*- coding: utf-8 -*-
# (C) 2021 UuuNyaa <UuuNyaa@gmail.com>

from abc import ABC, abstractmethod
from typing import NamedTuple

class TunerABC(ABC):
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

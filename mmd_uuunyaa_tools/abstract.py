# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import NamedTuple

class TunerABC(ABC):
    @abstractmethod
    def execute(self):
        pass

    @classmethod
    @abstractmethod
    def get_name(cls):
        pass


class TunerDescription(NamedTuple):
    tuner: type
    icon_filename: str

# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from abc import ABC, abstractmethod
from typing import NamedTuple


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

# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

# MMD UuuNyaa Tools is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# MMD UuuNyaa Tools is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import traceback

from mmd_uuunyaa_tools import auto_load

bl_info = {
    "name": "mmd_uuunyaa_tools",
    "description": "Utility tools for MMD model & scene editing by Uuu(/>ω<)/Nyaa!.",
    "author": "UuuNyaa",
    "version": (0, 5, 6),
    "blender": (2, 80, 0),
    "warning": "",
    "location": "View3D > Tool Shelf > MMD Tools Panel",
    "wiki_url": "https://github.com/UuuNyaa/blender_mmd_uuunyaa_tools/wiki",
    "tracker_url": "https://github.com/UuuNyaa/blender_mmd_uuunyaa_tools/issues",
    "support": "COMMUNITY",
    "category": "Object"
}

PACKAGE_PATH = os.path.dirname(__file__)
PACKAGE_NAME = __package__

REGISTER_HOOKS = []
UNREGISTER_HOOKS = []

auto_load.init()


def register():
    auto_load.register()
    for hook in REGISTER_HOOKS:
        try:
            hook()
        except:  # pylint: disable=bare-except
            traceback.print_exc()


def unregister():
    auto_load.unregister()

    for hook in UNREGISTER_HOOKS:
        try:
            hook()
        except:  # pylint: disable=bare-except
            traceback.print_exc()

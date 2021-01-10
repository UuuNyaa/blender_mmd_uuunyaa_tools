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

from mmd_uuunyaa_tools import auto_load

bl_info = {
    "name": "mmd_uuunyaa_tools",
    "description": "Utility tools for MMD model & scene editing by Uuu(/>ω<)/Nyaa!.",
    "author": "UuuNyaa",
    "version": (0, 0, 5),
    "blender": (2, 80, 0),
    "warning": "",
    "location": "View3D > Tool Shelf > MMD Tools Panel",
    "wiki_url": "https://github.com/UuuNyaa/blender_mmd_uuunyaa_tools/wiki",
    "tracker_url": "https://github.com/UuuNyaa/blender_mmd_uuunyaa_tools/issues",
    "support": "COMMUNITY",
    "category": "Object"
}

auto_load.init()

def register():
    auto_load.register()

def unregister():
    auto_load.unregister()

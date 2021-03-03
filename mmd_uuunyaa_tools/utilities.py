# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import hashlib
import math
import os
import re

import bpy


def to_int32(value: int) -> int:
    return ((value & 0xffffffff) ^ 0x80000000) - 0x80000000


def strict_hash(text: str) -> int:
    return to_int32(int(hashlib.sha1(text.encode('utf-8')).hexdigest(), 16))


SI_PREFIXES = ['', ' k', ' M', ' G', ' T']


def to_human_friendly_text(number: float) -> str:
    if number == 0:
        return '0'

    prefix_index = max(
        0,
        min(
            len(SI_PREFIXES)-1,
            int(math.floor(math.log10(abs(number))/3))
        )
    )
    return f'{number / 10**(3 * prefix_index):.2f}{SI_PREFIXES[prefix_index]}'


def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences


def sanitize_path_fragment(path_fragment: str) -> str:
    illegalRe = r'[\/\?<>\\:\*\|"]'
    controlRe = r'[\x00-\x1f\x80-\x9f]'
    reservedRe = r'^\.+$'
    windowsReservedRe = r'^(con|prn|aux|nul|com[0-9]|lpt[0-9])(\..*)?$'
    windowsTrailingRe = r'[\. ]+$'

    return re.sub(
        windowsTrailingRe, '',
        re.sub(
            windowsReservedRe, '',
            re.sub(
                reservedRe, '',
                re.sub(
                    controlRe, '',
                    re.sub(
                        illegalRe, '',
                        path_fragment
                    )
                )
            )
        )
    )


def label_multiline(layout, text='', width=0):
    if text.strip() == '':
        return

    threshold = int(width / 5.5) if width > 0 else 35
    for line in text.split('\n'):
        while len(line) > threshold:
            space_index = line.rfind(' ', 0, threshold)
            layout.label(text=line[:space_index])
            line = line[space_index:].lstrip()
        layout.label(text=line)


class ObjectMarker:
    def __init__(self, mark_id: str):
        self.mark_id = mark_id

    def mark(self, obj, depth=0):
        obj[self.mark_id] = True

        if depth <= 0:
            return

        for child in obj.children:
            self.mark(child, depth=depth-1)

    def unmark(self, obj, depth=0):
        if self.is_marked(obj):
            del obj[self.mark_id]

        if depth <= 0:
            return

        for child in obj.children:
            self.unmark(child, depth=depth-1)

    def is_marked(self, obj) -> bool:
        return self.mark_id in obj


class ObjectAppender(ObjectMarker):
    def __init__(self, mark_id: str, blend_filename: str):
        super().__init__(mark_id)
        self.blend_filename = blend_filename

    def remove_objects(self, target_collection: bpy.types.Collection = None):
        target = target_collection if target_collection is not None else bpy.context.view_layer.active_layer_collection.collection

        if not self.is_marked(target):
            return

        for obj in target.objects.values():
            if not self.is_marked(obj):
                continue

            bpy.data.objects.remove(obj, do_unlink=True)

        self.unmark(target)

    def append_collection(self, collection_name: str):
        if collection_name not in bpy.data.collections:
            path = os.path.join(self.blend_filename)
            with bpy.data.libraries.load(path, link=False) as (_, data_to):
                data_to.collections = [collection_name]

        return bpy.data.collections[collection_name]

    def append_objects_from_collection(self, collection_name: str, target_collection: bpy.types.Collection = None):
        source = self.append_collection(collection_name)
        target = target_collection if target_collection is not None else bpy.context.view_layer.active_layer_collection.collection
        self.mark(target)
        for obj in source.objects.values():
            self.mark(obj)
            source.objects.unlink(obj)
            target.objects.link(obj)
        bpy.data.collections.remove(source)

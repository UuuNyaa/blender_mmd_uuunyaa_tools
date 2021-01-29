# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import glob
import json
import os
import tempfile
import traceback
from concurrent.futures import Future
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Set, Union

import bpy
from mmd_uuunyaa_tools import PACKAGE_NAME, REGISTER_HOOKS
from mmd_uuunyaa_tools.asset_search.store import (URL, Callback, Content,
                                                  ContentStore, StoreABC, Task)


class AssetType(Enum):
    MODEL_MMD = 'Model (.pmx)'
    MODEL_BLENDER = 'Model (.blend)'
    LIGHTING = 'Lighting'
    MATERIAL = 'Material'


class AssetDescription:
    def __init__(
        self,
        id: str,
        type: AssetType,
        url: str,
        name: str,
        tags: Set[str],
        updated_at: datetime,
        thumbnail_url: str,
        download_url: str,
        content_path: str,
        readme_path: str,
        aliases: Dict[str, str],
        note: str,
    ):
        self.id = id
        self.type = type
        self.url = url
        self.name = name
        self.tags = tags
        self.updated_at = updated_at
        self.thumbnail_url = thumbnail_url
        self.download_url = download_url
        self.content_path = content_path
        self.readme_path = readme_path
        self.aliases = aliases
        self.note = note
        self.keywords = '^'.join(['', name, note, *tags, *aliases.values()]).lower()

    def tags_text(self) -> str:
        return ', '.join(self.tags)


class AssetRegistry:
    def __init__(self, *assets: AssetDescription):
        self.assets: Dict[str, AssetDescription] = {}
        for asset in assets:
            self.add(asset)

    def add(self, asset: AssetDescription):
        self.assets[asset.id] = asset

    def __getitem__(self, id: int):
        return self.assets[id]

    def items(self):
        return self.assets.items()

    def values(self):
        return self.assets.values()

    def reload(self, asset_jsons_path: str):
        self.assets.clear()

        for json_path in glob.glob(os.path.join(asset_jsons_path, '*.json')):
            try:
                with open(json_path) as f:
                    for asset in json.load(f)['assets']:
                        self.add(AssetDescription(
                            id=asset['id'],
                            type=AssetType[asset['type']],
                            url=asset['url'],
                            name=asset['name'],
                            tags=set(asset['tags'].values()),
                            updated_at=datetime.strptime(asset['updated_at'], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=timezone.utc).astimezone(tz=None),
                            thumbnail_url=asset['thumbnail_url'],
                            download_url=asset['download_url'],
                            content_path=asset['content_path'],
                            readme_path=asset['readme_path'],
                            aliases=asset['aliases'],
                            note=asset['note'],
                        ))
            except:
                traceback.print_exc()


ASSETS = AssetRegistry()
REGISTER_HOOKS.append(lambda: ASSETS.reload(bpy.context.preferences.addons[PACKAGE_NAME].preferences.asset_jsons_folder))


class ReloadableContentStore(StoreABC):
    _store: StoreABC = None

    def __init__(self):
        pass

    def reload(self, store):
        old_store = self._store
        self._store = store

        if old_store:
            del old_store

    def cancel_fetch(self, url: URL):
        self._store.cancel_fetch(url)

    def try_get_content(self, url: URL) -> Union[Content, None]:
        return self._store.try_get_content(url)

    def try_get_task(self, url: URL) -> Union[Task, None]:
        return self._store.try_get_task(url)

    def async_get_content(self, url: URL, callback: Callback) -> Future:
        return self._store.async_get_content(url, callback)


CONTENT_STORE = ReloadableContentStore()


def initialize_content_store():
    preferences = bpy.context.preferences.addons[PACKAGE_NAME].preferences
    cache_dir = preferences.cache_folder
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)

    global CONTENT_STORE
    CONTENT_STORE.reload(ContentStore(
        cache_dir=cache_dir,
        cache_limit_size=preferences.max_cache_size*1024*1024,
        temporary_dir=tempfile.mkdtemp(),
    ))
    print('initialize_content_store')


REGISTER_HOOKS.append(initialize_content_store)

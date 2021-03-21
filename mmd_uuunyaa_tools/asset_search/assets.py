# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import ast
import functools
import glob
import importlib
import json
import os
import pathlib
import shutil
import stat
import traceback
import zipfile
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Set, Union

import bpy
from mmd_uuunyaa_tools import PACKAGE_PATH, REGISTER_HOOKS
from mmd_uuunyaa_tools.utilities import get_preferences


class AssetType(Enum):
    ALL = 'All'
    MODEL_MMD = 'Model (.pmx)'
    MODEL_BLENDER = 'Model (.blend)'
    MOTION_MMD = 'Motion (.vmd)'
    POSE_MMD = 'Pose (.vpd)'
    LIGHTING = 'Lighting'
    MATERIAL = 'Material'


class AssetDescription:
    def __init__(
        self,
        id: str,
        type: AssetType,
        url: str,
        name: str,
        tags: Dict[str, str],
        updated_at: datetime,
        thumbnail_url: str,
        download_url: str,
        import_action: str,
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
        self.import_action = import_action
        self.aliases = aliases
        self.note = note
        self.tag_names = set(tags.values())
        self.keywords = '^'.join(['', name, note, *self.tag_names, *aliases.values()]).lower()

    def tags_text(self) -> str:
        return ', '.join(self.tag_names)


class _Utilities:
    @staticmethod
    def unzip(zip_file_path=None, encoding='cp437', password=None, asset=None):
        asset_path, asset_json = _Utilities.resolve_path(asset)

        print(f'unzip({zip_file_path},{asset_path},{asset_json})')

        if _Utilities.is_extracted(asset):
            return

        with zipfile.ZipFile(zip_file_path) as zip:
            for info in zip.infolist():
                orig_codec = 'utf-8' if info.flag_bits & 0x800 else 'cp437'
                info.filename = info.orig_filename.encode(orig_codec).decode(encoding)
                if os.sep != '/' and os.sep in info.filename:
                    info.filename = info.filename.replace(os.sep, '/')
                zip.extract(info, path=asset_path, pwd=password)

        _Utilities.write_json(asset)
        _Utilities.chmod_recursively(asset_path, stat.S_IWRITE)

    @staticmethod
    def unrar(rar_file_path=None, password=None, asset=None):
        asset_path, asset_json = _Utilities.resolve_path(asset)

        print(f'unrar({rar_file_path},{asset_path},{asset_json})')

        if _Utilities.is_extracted(asset):
            return

        namespace = 'rarfile'
        loader = importlib.machinery.SourceFileLoader(namespace, os.path.join(PACKAGE_PATH, 'externals', 'rarfile', 'rarfile.py'))
        rarfile = loader.load_module(namespace)

        try:
            with rarfile.RarFile(rar_file_path) as rar:
                rar.extractall(path=asset_path, pwd=password)
        except rarfile.RarCannotExec:
            raise rarfile.RarCannotExec('Failed to execute unrar or WinRAR\nPlease install unrar or WinRAR and setup the PATH properly.')

        _Utilities.write_json(asset)
        _Utilities.chmod_recursively(asset_path, stat.S_IWRITE)

    @staticmethod
    def link(from_path=None, to_name=None, asset=None):
        asset_path, asset_json = _Utilities.resolve_path(asset)

        print(f'link({from_path},{to_name},{asset_path},{asset_json})')

        if _Utilities.is_extracted(asset):
            return

        os.link(from_path, os.path.join(asset_path, to_name))

        _Utilities.write_json(asset)
        _Utilities.chmod_recursively(asset_path, stat.S_IWRITE)

    @staticmethod
    def chmod_recursively(path, mode):
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                target = os.path.join(root, dir)
                os.chmod(target, os.stat(target).st_mode | mode)

            for file in files:
                target = os.path.join(root, file)
                os.chmod(target, os.stat(target).st_mode | mode)

    @staticmethod
    def import_collection(blend_file_path, collection_name, asset=None):
        asset_path, _ = _Utilities.resolve_path(asset)

        print(f'import_collection({blend_file_path},{collection_name},{asset_path})')
        bpy.ops.wm.append(
            # 'INVOKE_DEFAULT',
            # filepath=os.path.join(asset_path, blend_file_path, 'Collection', collection_name),
            directory=os.path.join(asset_path, blend_file_path, 'Collection'),
            filename=collection_name,
        )

    @staticmethod
    def import_pmx(pmx_file_path, scale=0.08, asset=None):
        asset_path, _ = _Utilities.resolve_path(asset)

        print(f'import_pmx({pmx_file_path},{scale},{asset_path})')
        bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT', filepath=os.path.join(asset_path, pmx_file_path), scale=scale)

    @staticmethod
    def import_vmd(vmd_file_path, scale=0.08, asset=None):
        asset_path, _ = _Utilities.resolve_path(asset)

        print(f'import_vmd({vmd_file_path},{scale},{asset_path})')
        bpy.ops.mmd_tools.import_vmd('INVOKE_DEFAULT', filepath=os.path.join(asset_path, vmd_file_path), scale=scale)

    @staticmethod
    def import_vpd(vpd_file_path, scale=0.08, asset=None):
        asset_path, _ = _Utilities.resolve_path(asset)

        print(f'import_vpd({vpd_file_path},{scale},{asset_path})')
        bpy.ops.mmd_tools.import_vpd('INVOKE_DEFAULT', filepath=os.path.join(asset_path, vpd_file_path), scale=scale)

    class Visitor(ast.NodeVisitor):
        def visit(self, node: ast.AST):
            node_name = node.__class__.__name__

            if node_name not in {'Module', 'Expr', 'Call', 'Name', 'Str', 'JoinedStr', 'FormattedValue', 'Load', 'Num', 'keyword'}:
                raise NotImplementedError(ast.dump(node))

            if node_name == 'Call':
                if node.func.id not in {'unzip', 'unrar', 'import_collection', 'import_pmx', 'import_vmd'}:
                    raise NotImplementedError(ast.dump(node))

            return self.generic_visit(node)

    @staticmethod
    def to_dict(asset: AssetDescription) -> Dict[str, Any]:
        return {
            'id': asset.id,
            'type': asset.type,
            'url': asset.url,
            'name': asset.name,
            'tags': asset.tags,
            'updated_at': asset.updated_at,
            'thumbnail_url': asset.thumbnail_url,
            'download_url': asset.download_url,
            'import_action': asset.import_action,
            'aliases': asset.aliases,
            'note': asset.note,
        }

    @staticmethod
    def from_dict(asset: Dict[str, Any]) -> AssetDescription:
        return AssetDescription(
            id=asset['id'],
            type=AssetType[asset['type']],
            url=asset['url'],
            name=asset['name'],
            tags=asset['tags'],
            updated_at=datetime.strptime(asset['updated_at'], '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=timezone.utc).astimezone(tz=None),
            thumbnail_url=asset['thumbnail_url'],
            download_url=asset['download_url'],
            import_action=asset['import_action'],
            aliases=asset['aliases'],
            note=asset['note'],
        )

    @staticmethod
    def to_json(asset: AssetDescription, **kwargs):
        def encoder(obj):
            if isinstance(obj, datetime):
                return obj.astimezone(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            elif isinstance(obj, Enum):
                return obj.name
            elif isinstance(obj, set):
                return list(obj)

            raise TypeError(repr(obj) + ' is not JSON serializable')

        return json.dumps({
            'format': 'blender_mmd_assets:1',
            'description': 'This file is a mmd_uuunyaa_tools marking',
            'license': 'CC-BY-4.0 License',
            'created_at': datetime.now(),
            'assets': [_Utilities.to_dict(asset)]
        }, default=encoder, **kwargs)

    @staticmethod
    def to_context(asset: AssetDescription) -> Dict[str, str]:
        return {
            'id': asset.id,
            'type': asset.type.name,
            'name': asset.name,
            'aliases': asset.aliases,
        }

    @staticmethod
    def resolve_path(asset: AssetDescription) -> (str, str):
        preferences = get_preferences()
        asset_extract_root_folder = preferences.asset_extract_root_folder
        asset_extract_folder = preferences.asset_extract_folder
        asset_extract_json = preferences.asset_extract_json

        context = _Utilities.to_context(asset)
        asset_path = os.path.join(
            asset_extract_root_folder,
            asset_extract_folder.format(**context)
        )

        asset_json = os.path.join(
            asset_path,
            asset_extract_json.format(**context)
        )

        return (asset_path, asset_json)

    @staticmethod
    def is_extracted(asset: AssetDescription) -> bool:
        _, asset_json = _Utilities.resolve_path(asset)
        return os.path.exists(asset_json)

    @staticmethod
    def write_json(asset: AssetDescription):
        _, asset_json = _Utilities.resolve_path(asset)
        try:
            with open(asset_json, mode='wt', encoding='utf-8') as f:
                f.write(_Utilities.to_json(asset, indent=2, ensure_ascii=False))
        except:
            os.remove(asset_json)
            raise

    @staticmethod
    def execute_import_action(asset: AssetDescription, target_file: Union[str, None]):
        tree = ast.parse(asset.import_action)

        _Utilities.Visitor().visit(tree)

        exec(compile(tree, '<source>', 'exec'), {'__builtins__': {}}, {
            'unzip': functools.partial(_Utilities.unzip, zip_file_path=target_file, asset=asset),
            'unrar': functools.partial(_Utilities.unrar, rar_file_path=target_file, asset=asset),
            'import_collection': functools.partial(_Utilities.import_collection, asset=asset),
            'import_pmx': functools.partial(_Utilities.import_pmx, asset=asset),
            'import_vmd': functools.partial(_Utilities.import_vmd, asset=asset),
            'import_vpd': functools.partial(_Utilities.import_vpd, asset=asset),
        })


class AssetRegistry:

    def __init__(self, *assets: AssetDescription):
        self.assets: Dict[str, AssetDescription] = {}
        for asset in assets:
            self.add(asset)

    def add(self, asset: AssetDescription):
        self.assets[asset.id] = asset

    def __getitem__(self, id: str):
        return self.assets[id]

    def items(self):
        return self.assets.items()

    def values(self):
        return self.assets.values()

    def reload(self, asset_jsons_folder: str):
        self.assets.clear()

        json_paths = glob.glob(os.path.join(asset_jsons_folder, '*.json'))
        json_paths.sort()
        for json_path in json_paths:
            try:
                with open(json_path, encoding='utf-8') as f:
                    for asset in json.load(f)['assets']:
                        self.add(_Utilities.from_dict(asset))
            except:
                traceback.print_exc()

    def is_extracted(self, id: str) -> bool:
        # TODO cache
        return _Utilities.is_extracted(self[id])

    def resolve_path(self, id: str) -> str:
        # TODO cache
        asset_dir, _ = _Utilities.resolve_path(self[id])
        return asset_dir

    def execute_import_action(self, id: str, target_file: Union[str, None]):
        _Utilities.execute_import_action(self[id], target_file)


ASSETS = AssetRegistry()


def initialize_asset_registory():
    preferences = get_preferences()
    ASSETS.reload(preferences.asset_jsons_folder)


REGISTER_HOOKS.append(initialize_asset_registory)

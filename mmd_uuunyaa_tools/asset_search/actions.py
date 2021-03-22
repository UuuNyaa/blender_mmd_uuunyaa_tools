# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import ast
import functools
import importlib
import os
import pathlib
import stat
import zipfile
from typing import List, Union

import bpy
import requests
from mmd_uuunyaa_tools import PACKAGE_PATH, REGISTER_HOOKS
from mmd_uuunyaa_tools.asset_search.assets import AssetDescription, _Utilities


class RestrictionChecker(ast.NodeVisitor):
    def __init__(self, *functions: List[str]):
        self._functions = functions

    def visit(self, node: ast.AST):
        node_name = node.__class__.__name__

        if node_name not in {'Module', 'Expr', 'Call', 'Name', 'Str', 'JoinedStr', 'FormattedValue', 'Load', 'Num', 'keyword'}:
            raise NotImplementedError(ast.dump(node))

        if node_name == 'Call':
            if node.func.id not in self._functions:
                raise NotImplementedError(ast.dump(node))

        return self.generic_visit(node)


class DownloadActionExecutor:
    @staticmethod
    def get(url: str) -> requests.models.Response:
        return requests.get(url, stream=True)

    @staticmethod
    def tstorage(url: str, password: str = None) -> requests.models.Response:
        return requests.post(
            url,
            data={
                'op': 'download2',
                'id': url[len('http://tstorage.info/'):],
                'rand': '',
                'referer': '',
                'method_free': '',
                'method_premium': '',
                'password': password,
            },
            allow_redirects=True,
            stream=True
        )

    @staticmethod
    def execute_action(download_action: str):
        tree = ast.parse(download_action)

        functions = {
            'get': functools.partial(DownloadActionExecutor.get),
            'tstorage': functools.partial(DownloadActionExecutor.tstorage),
        }

        RestrictionChecker(*(functions.keys())).visit(tree)

        ast.dump(tree)
        return eval(
            download_action,
            {'__builtins__': {}},
            {
                **functions
            }
        )


class ImportActionExecutor:
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
        ImportActionExecutor.chmod_recursively(asset_path, stat.S_IWRITE)

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
        ImportActionExecutor.chmod_recursively(asset_path, stat.S_IWRITE)

    @staticmethod
    def link(from_path=None, to_name=None, asset=None):
        asset_path, asset_json = _Utilities.resolve_path(asset)

        print(f'link({from_path},{to_name},{asset_path},{asset_json})')

        if _Utilities.is_extracted(asset):
            return

        os.link(from_path, os.path.join(asset_path, to_name))

        _Utilities.write_json(asset)
        ImportActionExecutor.chmod_recursively(asset_path, stat.S_IWRITE)

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

    @staticmethod
    def execute_import_action(asset: AssetDescription, target_file: Union[str, None]):
        tree = ast.parse(asset.import_action)

        functions = {
            'unzip': functools.partial(ImportActionExecutor.unzip, zip_file_path=target_file, asset=asset),
            'unrar': functools.partial(ImportActionExecutor.unrar, rar_file_path=target_file, asset=asset),
            'import_collection': functools.partial(ImportActionExecutor.import_collection, asset=asset),
            'import_pmx': functools.partial(ImportActionExecutor.import_pmx, asset=asset),
            'import_vmd': functools.partial(ImportActionExecutor.import_vmd, asset=asset),
            'import_vpd': functools.partial(ImportActionExecutor.import_vpd, asset=asset),
        }

        RestrictionChecker(*(functions.keys())).visit(tree)

        exec(
            compile(tree, '<source>', 'exec'),
            {'__builtins__': {}},
            {
                **functions
            }
        )

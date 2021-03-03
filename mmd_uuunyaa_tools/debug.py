# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

import importlib
import io
import json
import os
import zipfile

import requests

from mmd_uuunyaa_tools import PACKAGE_PATH


def debug_assets(*issue_numbers, repo='UuuNyaa/blender_mmd_assets'):
    namespace = 'cat_asset_json'
    loader = importlib.machinery.SourceFileLoader(namespace, os.path.join(PACKAGE_PATH, 'externals', 'blender_mmd_assets', 'cat_asset_json.py'))
    cat_asset_json = loader.load_module(namespace)
    session = requests.Session()

    assets = cat_asset_json.wrap_assets([
        cat_asset_json.fetch_asset(session, repo, issue_number)
        for issue_number in issue_numbers
    ])

    with open(os.path.join(PACKAGE_PATH, 'asset_jsons', 'ZDEBUG.json'), mode='wt', encoding='utf-8') as f:
        json.dump(assets, f, ensure_ascii=False, indent=2)

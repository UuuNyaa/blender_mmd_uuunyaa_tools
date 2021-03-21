# -*- coding: utf-8 -*-
# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD UuuNyaa Tools.

from abc import ABC, abstractmethod

import requests


class URLResolverABC(ABC):
    @abstractmethod
    def resolve(self, url: str) -> requests.models.Response:
        pass


class URLResolver(URLResolverABC):
    def resolve(self, url: str) -> requests.models.Response:
        if url.startswith('http://tstorage.info/'):
            return requests.post(
                url,
                data={
                    'op': 'download2',
                    'id': url[len('http://tstorage.info/'):],
                    'rand': '',
                    'referer': '',
                    'method_free': '',
                    'method_premium': '',
                },
                allow_redirects=True,
                stream=True
            )

        return requests.get(url, stream=True)

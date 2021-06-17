# -*- coding=UTF-8 -*-
# pyright: strict
"""Simple plugin system, user can do what they want in install method.  """


from importlib.machinery import SourceFileLoader
from typing import Dict
from abc import ABC, abstractmethod

from pathlib import Path

import importlib.util

import cast_unknown as cast


class Plugin(ABC):
    @abstractmethod
    def install(self) -> None:
        ...


class g:
    PLUGINS: Dict[str, Plugin] = {}
    PATH: str = ""


def register(name: str, plugin: Plugin) -> None:
    if name in g.PLUGINS:
        raise ValueError("plugin.register: duplicated name is not allowed: %s" % name)
    g.PLUGINS[name] = plugin


def reload():
    g.PLUGINS.clear()
    for i in Path(g.PATH).glob("*.py"):
        spec = importlib.util.spec_from_file_location(__name__, i)
        assert spec
        module = importlib.util.module_from_spec(spec)
        loader = cast.instance(spec.loader, SourceFileLoader)
        loader.exec_module(module)


def install(name: str) -> None:
    g.PLUGINS[name].install()

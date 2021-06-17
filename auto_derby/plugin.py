# -*- coding=UTF-8 -*-
# pyright: strict
"""Simple plugin system, user can do what they want in install method.  """


import importlib.util
import logging
from abc import ABC, abstractmethod
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import Dict

import cast_unknown as cast

LOGGER = logging.getLogger(__name__)


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
        spec = importlib.util.spec_from_file_location(i.stem, i)
        assert spec
        module = importlib.util.module_from_spec(spec)
        loader = cast.instance(spec.loader, SourceFileLoader)
        loader.exec_module(module)
    LOGGER.debug("loaded: %s", ", ".join(g.PLUGINS.keys()))


def install(name: str) -> None:
    g.PLUGINS[name].install()
    LOGGER.info("installed: %s", name)

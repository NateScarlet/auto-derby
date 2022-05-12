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

from . import app


class Plugin(ABC):
    @abstractmethod
    def install(self) -> None:
        ...


class _g:
    deprecations: Dict[str, str] = {}


class g:
    plugins: Dict[str, Plugin] = {}
    path: str = ""


def register(name: str, plugin: Plugin) -> None:
    if name in g.plugins:
        raise ValueError("plugin.register: duplicated name is not allowed: %s" % name)
    g.plugins[name] = plugin


def reload():
    g.plugins.clear()
    for i in Path(g.path).glob("*.py"):
        spec = importlib.util.spec_from_file_location(i.stem, i)
        assert spec
        module = importlib.util.module_from_spec(spec)
        loader = cast.instance(spec.loader, SourceFileLoader)
        loader.exec_module(module)
    app.log.text("loaded: %s" % ", ".join(g.plugins.keys()), level=app.DEBUG)


def deprecate(name: str, reason: str):
    _g.deprecations[name] = reason


def is_deprecated(name: str) -> bool:
    return name in _g.deprecations


def get_deprecation_reason(name: str) -> str:
    return _g.deprecations.get(name, "")


def install(name: str) -> None:
    if is_deprecated(name):
        app.log.text(
            f"plugin '{name}' is deprecated: {get_deprecation_reason(name)}",
            level=app.WARN,
        )
    g.plugins[name].install()
    app.log.text("installed: %s" % name, level=app.DEBUG)


# DEPRECATED
globals()["LOGGER"] = logging.getLogger(__name__)

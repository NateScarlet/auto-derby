# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, Optional, Text

from .globals import g
from .item import Item


class _g:
    load_key: Any = None
    items: Dict[int, Item] = {}


def _load_key():
    return g.data_path


def _iter(p: Text):
    with open(p, "r", encoding="utf-8") as f:
        for i in f:
            yield Item.from_dict(json.loads(i))


def reload():
    _g.items = {i.id: i for i in _iter(g.data_path)}
    _g.load_key = _load_key()


def reload_on_demand() -> None:
    if _g.load_key != _load_key():
        reload()


def get(id: int) -> Optional[Item]:
    reload_on_demand()
    return _g.items.get(id)


def iterate() -> Iterator[Item]:
    reload_on_demand()
    for i in _g.items.values():
        yield i

# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import json
from typing import Any, Dict, Iterator, Text

from .globals import g
from .item import Item


class _g:
    load_key: Any = None
    item_data: Dict[int, Dict[Text, Any]] = {}


def _load_key():
    return g.data_path


def _iter(p: Text):
    with open(p, "r", encoding="utf-8") as f:
        for i in f:
            yield json.loads(i)


def reload():
    _g.item_data = {i["id"]: i for i in _iter(g.data_path)}
    _g.load_key = _load_key()


def reload_on_demand() -> None:
    if _g.load_key != _load_key():
        reload()


def get(id: int) -> Item:
    reload_on_demand()
    v = _g.item_data.get(id)
    if v is None:
        v = Item.new()
        v.id = id
        return v
    return Item.from_dict(v)


def iterate() -> Iterator[Item]:
    reload_on_demand()
    for i in _g.item_data.values():
        yield Item.from_dict(i)

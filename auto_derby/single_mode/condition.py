# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations
import json
from typing import Any, Dict, Iterator, Text

from .. import data


class g:
    data_path: Text = data.path("single_mode_conditions.jsonl")


class Condition:
    def __init__(self):
        self.id = 0
        self.name = ""
        self.description = ""

    def to_dict(self):
        d = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }
        return d

    @classmethod
    def from_dict(cls, d: Dict[Text, Any]) -> Condition:
        c = cls()
        c.id = d["id"]
        c.name = d["name"]
        c.description = d["description"]
        return c


class _g:
    load_key: Any = None
    condition_data: Dict[int, Dict[Text, Any]] = {}


def _load_key():
    return g.data_path


def _iter(p: Text):
    with open(p, "r", encoding="utf-8") as f:
        for i in f:
            yield json.loads(i)


def reload():
    _g.condition_data = {i["id"]: i for i in _iter(g.data_path)}
    _g.load_key = _load_key()


def reload_on_demand() -> None:
    if _g.load_key != _load_key():
        reload()


def get(id: int) -> Condition:
    reload_on_demand()
    v = _g.condition_data.get(id)
    if v is None:
        v = Condition()
        v.id = id
        v.name = f"unknown({id})"
        return v
    return Condition.from_dict(v)


def iterate() -> Iterator[Condition]:
    reload_on_demand()
    for i in _g.condition_data.values():
        yield Condition.from_dict(i)

# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, Text, Tuple

from PIL.Image import Image

from .. import data, imagetools, terminal

_LOGGER = logging.getLogger(__name__)


# TODO: add config
class g:
    data_path: Text = data.path("single_mode_items.jsonl")
    label_path: Text = ""
    items: Dict[int, Item] = {}


class _g:
    loaded_data_path: Text = ""
    labels = imagetools.CSVImageHashMap(int)


class ItemEffect:
    def __init__(self) -> None:
        self.id = 0
        self.group = 0
        self.type = 0
        self.values = (0, 0, 0, 0)
        self.turn_count = 0

    def to_dict(self) -> Dict[Text, Any]:
        d = {
            "id": self.id,
            "group": self.group,
            "type": self.type,
            "values": self.values,
            "turnCount": self.turn_count,
        }
        return d

    @classmethod
    def from_dict(cls, d: Dict[Text, Any]) -> ItemEffect:
        v = cls()
        v.id = d["id"]
        v.group = d["group"]
        v.type = d["type"]
        v.values = tuple(d["values"])
        v.turn_count = d["turnCount"]

        return v


class Item:
    def __init__(self) -> None:
        self.id = 0
        self.name = ""
        self.description = ""
        self.original_price = 0
        self.max_quantity = 0
        self.effect_priority = 0
        self.effects: Tuple[ItemEffect, ...] = ()

        # dynamic data
        self.price = 0
        self.quantity = 0

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Item) and self.id == other.id

    def __str__(self):
        return f"Item<{self.id}:{self.name}>"

    def to_dict(self) -> Dict[Text, Any]:
        d = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "originalPrice": self.original_price,
            "maxQuantity": self.max_quantity,
            "effectPriority": self.effect_priority,
            "effects": [i.to_dict() for i in self.effects],
        }
        return d

    @classmethod
    def from_dict(cls, d: Dict[Text, Any]) -> Item:
        v = cls()
        v.id = d["id"]
        v.name = d["name"]
        v.description = d["description"]
        v.original_price = d["originalPrice"]
        v.max_quantity = d["maxQuantity"]
        v.effect_priority = d["effectPriority"]
        v.effects = tuple(ItemEffect.from_dict(i) for i in d["effects"])
        return v


def _iter(p: Text):
    with open(p, "r", encoding="utf-8") as f:
        for i in f:
            yield Item.from_dict(json.loads(i))


def reload():
    g.items = {i.id: i for i in _iter(g.data_path)}
    _g.labels.clear()
    try:
        _g.labels.load_once(data.path("single_mode_item_labels.csv"))
    except FileNotFoundError:
        pass
    try:
        _g.labels.load_once(g.label_path)
    except FileNotFoundError:
        pass
    _g.labels.save_path = g.label_path
    return


def reload_on_demand() -> None:
    if _g.loaded_data_path != g.data_path:
        reload()


def get(id: int) -> Optional[Item]:
    reload_on_demand()
    return g.items.get(id)


def _cast_int(v: Text, d: int) -> int:
    try:
        return int(v)
    except ValueError:
        return d


def _prompt(img: Image, h: Text, value: Optional[Item], similarity: float) -> Item:
    if terminal.g.prompt_disabled:
        # avoid show image during loop
        raise terminal.PromptDisabled
    close_img = imagetools.show(img, h)
    try:
        ans = ""
        while value and ans not in ("Y", "N"):
            ans = terminal.prompt(
                f"Matching current displaying image: value={value}, similarity={similarity:0.3f}.\n"
                "Is this correct? (Y/N)"
            ).upper()
        if ans == "Y":
            ret = value
        else:
            ret = get(
                _cast_int(
                    terminal.prompt(
                        "Item id for current displaying image\n"
                        '(see "auto_derby/data/single_mode_items.jsonl"):'
                    ),
                    0,
                )
            )
    finally:
        close_img()
    if not ret:
        return _prompt(img, h, value, similarity)
    _g.labels.label(h, ret.id)
    _LOGGER.info("labeled: hash=%s, value=%s", h, ret)
    return ret


def from_title_image(img: Image, threshold: float = 0.8) -> Item:
    reload_on_demand()
    h = imagetools.image_hash(img, divide_x=4)
    if _g.labels.is_empty():
        return _prompt(img, h, None, 0)
    res = _g.labels.query(h)
    _LOGGER.debug(
        "match label: search=%s, result=%s",
        h,
        res,
    )
    item = get(res.value)
    if item and res.similarity > threshold:
        return item
    return _prompt(img, h, item, res.similarity)

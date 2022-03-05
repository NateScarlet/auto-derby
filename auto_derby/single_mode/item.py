# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import io
import json
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Text, Tuple

from PIL.Image import Image

from .. import data, imagetools, web
from ..constants import TrainingType
from .context import Context

if TYPE_CHECKING:
    from .commands import Command

_LOGGER = logging.getLogger(__name__)


# TODO: add config
class g:
    data_path: Text = data.path("single_mode_items.jsonl")
    label_path: Text = ""
    items: Dict[int, Item] = {}


class _g:
    loaded_data_path: Text = ""
    labels = imagetools.CSVImageHashMap(int)


class Effect:
    TYPE_PROPERTY = 1
    TYPE_TRAINING_LEVEL = 2
    TYPE_FRIENDSHIP = 3
    TYPE_CONDITION = 6
    TYPE_RESET_PARTER = 10
    TYPE_TRAINING_BUFF = 11
    TYPE_TRAINING_VITALITY_DEBUFF = 12
    TYPE_TRAINING_NO_FAILURE = 10
    TYPE_RACE_BUFF = 14

    PROPERTY_SPEED = 1
    PROPERTY_STAMINA = 2
    PROPERTY_POWER = 3
    PROPERTY_GUTS = 4
    PROPERTY_WISDOM = 5
    PROPERTY_VITALITY = 10
    PROPERTY_MAX_VITALITY = 11
    PROPERTY_MOOD = 20

    TRAINING_LEVEL_SPEED = 101
    TRAINING_LEVEL_STAMINA = 105
    TRAINING_LEVEL_POWER = 102
    TRAINING_LEVEL_GUTS = 103
    TRAINING_LEVEL_WISDOM = 106

    CONDITION_ADD = 1
    CONDITION_REMOVE = 2

    RACE_BUFF_REWARD = 6
    RACE_BUFF_FAN = 40

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
    def from_dict(cls, d: Dict[Text, Any]) -> Effect:
        v = cls()
        v.id = d["id"]
        v.group = d["group"]
        v.type = d["type"]
        v.values = tuple(d["values"])
        v.turn_count = d["turnCount"]

        return v


_effect_transforms: List[_EffectTransform] = []


class EffectSummary:
    def __init__(self) -> None:
        self.speed = 0
        self.statmia = 0
        self.power = 0
        self.guts = 0
        self.wisdom = 0
        self.vitality = 0
        self.max_vitality = 0
        self.mood = 0
        self.add_conditions: Tuple[int, ...] = ()
        self.remove_conditions: Tuple[int, ...] = ()
        self.training_level: Dict[TrainingType, float] = {}
        self.training_buff: Dict[TrainingType, float] = {}
        self.training_vitality_debuff: Dict[TrainingType, float] = {}
        self.reset_parters = False
        self.no_training_failure = False
        self.race_fan_buff = 0
        self.race_reward_buff = 0

        self.unknown_effects: Tuple[Effect, ...] = ()

    def add(self, effect: Effect):
        for i in _effect_transforms:
            if i(effect, self):
                break
        else:
            self.unknown_effects += (effect,)


_EffectTransform = Callable[[Effect, EffectSummary], bool]


def _only_effect_type(effect_type: int):
    def _wrapper(fn: _EffectTransform) -> _EffectTransform:
        def _func(effect: Effect, summary: EffectSummary) -> bool:
            if effect.type != effect_type:
                return False
            return fn(effect, summary)

        return _func

    return _wrapper


def _register_transform(fn: _EffectTransform):
    _effect_transforms.append(fn)
    return fn


@_register_transform
@_only_effect_type(Effect.TYPE_PROPERTY)
def _(effect: Effect, summary: EffectSummary):
    return False


class Item:
    def __init__(self) -> None:
        self.id = 0
        self.name = ""
        self.description = ""
        self.original_price = 0
        self.max_quantity = 0
        self.effect_priority = 0
        self.effects: Tuple[Effect, ...] = ()

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
        v.effects = tuple(Effect.from_dict(i) for i in d["effects"])
        return v

    def exchange_score(self, ctx: Context) -> float:
        """
        Item will be exchanged if score greater than 0.
        """
        return 0

    def effect_score(self, ctx: Context, command: Command) -> float:
        """Item will be used before command if score greater than 0."""
        return 0

    def should_use_directly(self, ctx: Context) -> bool:
        """whether use after exchange."""
        return False


def _iter(p: Text):
    with open(p, "r", encoding="utf-8") as f:
        for i in f:
            yield Item.from_dict(json.loads(i))


def reload():
    g.items = {i.id: i for i in _iter(g.data_path)}
    _g.labels.clear()
    _g.labels.load_once(data.path("single_mode_item_labels.csv"))
    _g.labels.load_once(g.label_path)
    _g.labels.save_path = g.label_path
    return


def reload_on_demand() -> None:
    if _g.loaded_data_path != g.data_path:
        reload()


def get(id: int) -> Optional[Item]:
    reload_on_demand()
    return g.items.get(id)


def _prompt(img: Image, h: Text, defaultValue: int) -> Item:
    reload_on_demand()
    img_data = io.BytesIO()
    img.save(img_data, "PNG")

    form_data = web.prompt(
        web.page.render(
            {
                "type": "SINGLE_MODE_ITEM_SELECT",
                "imageURL": "/img.png",
                "defaultValue": defaultValue,
                "options": [i.to_dict() for i in g.items.values()],
            }
        ),
        web.page.ASSETS,
        web.Route("/img.png", web.Blob(img_data.getvalue(), "image/png")),
    )
    form_id = int(form_data["id"][0])
    ret = get(form_id)
    if not ret:
        raise ValueError("invalid item id: %s" % form_id)
    _g.labels.label(h, ret.id)
    _LOGGER.info("labeled: hash=%s, value=%s", h, ret)
    return ret


def from_title_image(img: Image, threshold: float = 0.8) -> Item:
    reload_on_demand()
    h = imagetools.image_hash(img, divide_x=4)
    if _g.labels.is_empty():
        return _prompt(img, h, 0)
    res = _g.labels.query(h)
    _LOGGER.debug(
        "match label: search=%s, result=%s",
        h,
        res,
    )
    item = get(res.value)
    if item and res.similarity > threshold:
        return item
    return _prompt(img, h, item.id if item else 0)

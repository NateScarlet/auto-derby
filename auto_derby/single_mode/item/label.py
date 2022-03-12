# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import io
import logging
from typing import Any, Text

from PIL.Image import Image


from ... import data, imagetools, web, texttools
from . import game_data
from .globals import g
from .item import Item

_LOGGER = logging.getLogger(__name__)


class _g:
    labels = imagetools.CSVImageHashMap(int)
    label_load_key: Any = None


def _load_key():
    return g.label_path


def reload():
    _g.labels.clear()
    _g.labels.load_once(data.path("single_mode_item_labels.csv"))
    _g.labels.load_once(g.label_path)
    _g.labels.save_path = g.label_path
    _g.label_load_key = _load_key()


def reload_on_demand() -> None:
    if _g.label_load_key != _load_key():
        reload()


def _prompt(img: Image, h: Text, defaultValue: int) -> Item:
    # TODO: allow disable
    img_data = io.BytesIO()
    img.save(img_data, "PNG")

    form_data = web.prompt(
        web.page.render(
            {
                "type": "SINGLE_MODE_ITEM_SELECT",
                "imageURL": "/img.png",
                "defaultValue": defaultValue,
                "options": [i.to_dict() for i in game_data.iterate()],
            }
        ),
        web.page.ASSETS,
        web.Route("/img.png", web.Blob(img_data.getvalue(), "image/png")),
    )
    form_id = int(form_data["id"][0])
    ret = game_data.get(form_id)
    if not ret:
        raise ValueError("invalid item id: %s" % form_id)
    _g.labels.label(h, ret.id)
    _LOGGER.info("labeled: hash=%s, value=%s", h, ret)
    return ret


def _default_name_label_similarity_threshold(item: Item) -> float:
    try:
        match = next(
            i
            for i in game_data.iterate()
            if 0.7 < texttools.compare(i.name, item.name) < 1
        )
        _LOGGER.debug(
            "use higher name label similarity threshold for %s due to similar item name: %s",
            item.name,
            match.name,
        )
        return 0.9
    except StopIteration:
        return 0.8


def _name_label_similarity_threshold(item: Item) -> float:
    if item.id not in g.name_label_similarity_threshold:
        g.name_label_similarity_threshold[
            item.id
        ] = _default_name_label_similarity_threshold(item)
    return g.name_label_similarity_threshold[item.id]


def from_name_image(img: Image) -> Item:
    reload_on_demand()
    h = imagetools.image_hash(img, divide_x=4)
    if _g.labels.is_empty():
        return _prompt(img, h, 0)
    res = _g.labels.query(h)
    _LOGGER.debug("query label: %s by %s", res, h)
    item = game_data.get(res.value)
    if item and res.similarity > _name_label_similarity_threshold(item):
        return item
    return _prompt(img, h, item.id if item else 0)

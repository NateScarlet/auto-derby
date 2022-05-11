# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import io
from typing import Any, Text
from uuid import uuid4

from PIL.Image import Image

from auto_derby import mathtools


from ... import data, imagetools, web, texttools, app
from . import game_data
from .globals import g
from .item import Item


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
    if g.prompt_disabled:
        ret = game_data.get(defaultValue)
        app.log.image("using low similarity item: %s" % ret, img, level=app.WARN)
        return ret
    img_data = io.BytesIO()
    imagetools.save_png(img, img_data)

    token = uuid4().hex
    form_data = web.prompt(
        web.page.render(
            {
                "type": "SINGLE_MODE_ITEM_SELECT",
                "imageURL": "/img.png",
                "submitURL": "?token=" + token,
                "defaultValue": defaultValue,
                "options": [i.to_dict() for i in game_data.iterate()],
            }
        ),
        web.page.ASSETS,
        web.Route("/img.png", web.Blob(img_data.getvalue(), "image/png")),
        web.middleware.TokenAuth(token, ("POST",)),
    )
    form_id = int(form_data["id"][0])
    ret = game_data.get(form_id)
    if not ret:
        raise ValueError("invalid item id: %s" % form_id)
    _g.labels.label(h, ret.id)
    app.log.image("labeled: hash=%s, value=%s" % (h, ret), img)
    return ret


def _default_name_label_similarity_threshold(item: Item) -> float:
    similarities_on_name = sorted(
        (
            (texttools.compare(i.name, item.name), i)
            for i in game_data.iterate()
            if i.name != item.name
        ),
        key=lambda x: -x[0],
    )
    if similarities_on_name:
        s, match = similarities_on_name[0]
    else:
        s, match = 0, None

    ret = mathtools.interpolate(
        int(s * 10000),
        (
            (0, 0.8),
            (7000, 0.8),
            (8000, 0.95),
            (10000, 1.0),
        ),
    )
    if ret > 0.8:
        app.log.text(
            "use higher name label similarity threshold %.2f for %s due to similar item name: %s"
            % (ret, item.name, match and match.name),
            level=app.DEBUG,
        )
    return ret


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
    app.log.image("query label: %s by %s" % (res, h), img, level=app.DEBUG)
    item = game_data.get(res.value)
    if item and res.similarity > _name_label_similarity_threshold(item):
        return item
    return _prompt(img, h, item.id if item else 0)

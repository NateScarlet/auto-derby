# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
import os
from typing import Iterator, Optional, Text, Tuple

import cv2
import numpy as np
from PIL.Image import Image

from ... import imagetools, mathtools
from ..context import Context
from .globals import g

_LOGGER = logging.getLogger(__name__)


def _recognize_type_color(rp: mathtools.ResizeProxy, icon_img: Image) -> int:
    type_pos = rp.vector2((7, 18), 540)
    type_colors = (
        ((36, 170, 255), Partner.TYPE_SPEED),
        ((255, 106, 86), Partner.TYPE_STAMINA),
        ((255, 151, 27), Partner.TYPE_POWER),
        ((255, 96, 156), Partner.TYPE_GUTS),
        ((3, 191, 126), Partner.TYPE_WISDOM),
        ((255, 179, 22), Partner.TYPE_FRIEND),
    )
    for color, v in type_colors:
        if imagetools.compare_color(icon_img.getpixel(type_pos), color) > 0.9:
            return v
    return Partner.TYPE_OTHER


def _recognize_has_hint(rp: mathtools.ResizeProxy, icon_img: Image) -> bool:
    bbox = rp.vector4((50, 0, 58, 8), 540)
    hint_mark_color = (127, 67, 255)
    hint_mark_img = icon_img.crop(bbox)
    hint_mask = imagetools.constant_color_key(
        imagetools.cv_image(hint_mark_img), hint_mark_color
    )
    return np.average(hint_mask) > 200


def _recognize_has_training(rp: mathtools.ResizeProxy, icon_img: Image) -> bool:
    bbox = rp.vector4((52, 0, 65, 8), 540)
    mark_color = (67, 131, 255)
    mark_img = icon_img.crop(bbox)
    mask = imagetools.constant_color_key(imagetools.cv_image(mark_img), mark_color)
    return np.average(mask) > 100


def _recognize_level(rp: mathtools.ResizeProxy, icon_img: Image) -> int:
    pos = (
        rp.vector2((10, 65), 540),  # level 1
        rp.vector2((20, 65), 540),  # level 2
        rp.vector2((33, 65), 540),  # level 3
        rp.vector2((43, 65), 540),  # level 4
        rp.vector2((55, 65), 540),  # level 5
    )
    colors = (
        (109, 108, 119),  # empty
        (42, 192, 255),  # level 1
        (42, 192, 255),  # level 2
        (162, 230, 30),  # level 3
        (255, 173, 30),  # level 4
        (255, 235, 120),  # level 5
    )
    spec: Tuple[Tuple[Tuple[Tuple[int, int], Tuple[int, int, int]], ...], ...] = (
        # level 0
        (
            (pos[0], colors[0]),
            (pos[1], colors[0]),
            (pos[2], colors[0]),
            (pos[3], colors[0]),
            (pos[4], colors[0]),
        ),
        # level 1
        (
            (pos[0], colors[1]),
            (pos[1], colors[0]),
            (pos[2], colors[0]),
            (pos[3], colors[0]),
            (pos[4], colors[0]),
        ),
        # level 2
        (
            (pos[0], colors[2]),
            (pos[1], colors[2]),
            (pos[3], colors[0]),
            (pos[4], colors[0]),
        ),
        # level 3
        (
            (pos[0], colors[3]),
            (pos[1], colors[3]),
            (pos[2], colors[3]),
            (pos[4], colors[0]),
        ),
        # level 4
        (
            (pos[0], colors[4]),
            (pos[1], colors[4]),
            (pos[2], colors[4]),
            (pos[3], colors[4]),
        ),
        # level 5
        (
            (pos[0], colors[5]),
            (pos[4], colors[5]),
        ),
    )

    for level, s in enumerate(spec):
        if all(
            imagetools.compare_color(
                icon_img.getpixel(pos),
                color,
            )
            > 0.9
            for pos, color in s
        ):
            return level
    return -1


class Partner:
    TYPE_SPEED: int = 1
    TYPE_STAMINA: int = 2
    TYPE_POWER: int = 3
    TYPE_GUTS: int = 4
    TYPE_WISDOM: int = 5
    TYPE_FRIEND: int = 6
    TYPE_OTHER: int = 7

    def __init__(self):
        self.level = 0
        self.type = 0
        self.has_hint = False
        self.has_training = False
        self.icon_bbox = (0, 0, 0, 0)

    def __str__(self):
        return (
            f"Partner<type={self.type_text(self.type)} lv={self.level} "
            f"hint={self.has_hint} training={self.has_training} icon_bbox={self.icon_bbox}>)"
        )

    def score(self, ctx: Context) -> float:
        if self.type == self.TYPE_OTHER:
            return 2 + self.level
        ret = mathtools.interpolate(
            ctx.turn_count(),
            (
                (0, 5),
                (24, 3),
                (48, 2),
                (72, 0),
            ),
        )
        if self.has_training:
            ret += 7
        return ret

    @staticmethod
    def new() -> Partner:
        return g.partner_class()

    @staticmethod
    def type_text(v: int) -> Text:
        return {
            Partner.TYPE_SPEED: "spd",
            Partner.TYPE_STAMINA: "sta",
            Partner.TYPE_POWER: "pow",
            Partner.TYPE_GUTS: "gut",
            Partner.TYPE_WISDOM: "wis",
            Partner.TYPE_FRIEND: "frd",
            Partner.TYPE_OTHER: "oth",
        }.get(v, f"unknown({v})")

    @classmethod
    def _from_training_scene_icon(
        cls, img: Image, bbox: Tuple[int, int, int, int]
    ) -> Optional[Partner]:
        rp = mathtools.ResizeProxy(img.width)
        icon_img = img.crop(bbox)
        if os.getenv("DEBUG") == __name__:
            _LOGGER.debug(
                "icon: img=%s",
                imagetools.image_hash(icon_img, save_path=g.image_path),
            )
            cv2.imshow("icon_img", imagetools.cv_image(icon_img))
            cv2.waitKey()
            cv2.destroyAllWindows()
        level = _recognize_level(rp, icon_img)
        if level < 0:
            return None
        self = cls.new()
        self.icon_bbox = bbox
        self.level = level
        self.has_hint = _recognize_has_hint(rp, icon_img)
        self.has_training = _recognize_has_training(rp, icon_img)
        self.type = _recognize_type_color(rp, icon_img)
        _LOGGER.debug("partner: %s", self)
        return self

    @classmethod
    def from_training_scene(cls, img: Image) -> Iterator[Partner]:
        rp = mathtools.ResizeProxy(img.width)

        icon_bbox = rp.vector4((448, 146, 516, 220), 540)
        icon_y_offset = rp.vector(90, 540)
        icons_bottom = rp.vector(578, 540)
        while icon_bbox[2] < icons_bottom:
            v = cls._from_training_scene_icon(img, icon_bbox)
            if not v:
                break
            yield v
            icon_bbox = (
                icon_bbox[0],
                icon_bbox[1] + icon_y_offset,
                icon_bbox[2],
                icon_bbox[3] + icon_y_offset,
            )


g.partner_class = Partner

# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

import logging
import os
from typing import Iterator, Optional, Text, Tuple

import cv2
import numpy as np
from PIL.Image import Image

from ... import imagetools, mathtools, template, templates
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
        if (
            imagetools.compare_color_near(
                imagetools.cv_image(icon_img), type_pos, color[::-1]
            )
            > 0.9
        ):
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


def _recognize_has_training(
    ctx: Context, rp: mathtools.ResizeProxy, icon_img: Image
) -> bool:
    if ctx.scenario != ctx.SCENARIO_AOHARU:
        return False
    bbox = rp.vector4((52, 0, 65, 8), 540)
    mark_img = icon_img.crop(bbox)
    mask = imagetools.constant_color_key(
        imagetools.cv_image(mark_img),
        (67, 131, 255),
        (82, 171, 255),
        threshold=0.9,
    )

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("training_mark_mask", mask)
        cv2.waitKey()
        cv2.destroyAllWindows()
        _LOGGER.debug("training mark mask: avg=%0.2f", np.average(mask))
    return np.average(mask) > 80


def _recognize_has_soul_burst(
    ctx: Context, rp: mathtools.ResizeProxy, icon_img: Image
) -> bool:
    if ctx.scenario != ctx.SCENARIO_AOHARU:
        return False
    bbox = rp.vector4((52, 0, 65, 8), 540)
    mark_img = icon_img.crop(bbox)
    mask = imagetools.constant_color_key(
        imagetools.cv_image(mark_img),
        (198, 255, 255),
        threshold=0.9,
    )

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("soul_burst_mark_mask", mask)
        cv2.waitKey()
        cv2.destroyAllWindows()
        _LOGGER.debug("soul burst mark mask: avg=%0.2f", np.average(mask))
    return np.average(mask) > 80


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
            imagetools.compare_color_near(
                imagetools.cv_image(icon_img),
                pos,
                color[::-1],
            )
            > 0.95
            for pos, color in s
        ):
            return level
    return -1


def _recognize_soul(
    rp: mathtools.ResizeProxy, screenshot: Image, icon_bbox: Tuple[int, int, int, int]
) -> float:
    right_bottom_icon_bbox = (
        icon_bbox[0] + rp.vector(49, 540),
        icon_bbox[1] + rp.vector(32, 540),
        icon_bbox[0] + rp.vector(74, 540),
        icon_bbox[1] + rp.vector(58, 540),
    )

    right_bottom_icon_img = screenshot.crop(right_bottom_icon_bbox)
    is_full = any(
        template.match(right_bottom_icon_img, templates.SINGLE_MODE_AOHARU_SOUL_FULL)
    )
    if is_full:
        return 1

    soul_bbox = (
        icon_bbox[0] - rp.vector(35, 540),
        icon_bbox[1] + rp.vector(33, 540),
        icon_bbox[0] + rp.vector(2, 540),
        icon_bbox[3] - rp.vector(0, 540),
    )
    img = screenshot.crop(soul_bbox)
    img = imagetools.resize(img, height=40)
    cv_img = imagetools.cv_image(img)
    blue_outline_img = imagetools.constant_color_key(
        cv_img,
        (251, 109, 0),
        (255, 178, 99),
        threshold=0.6,
    )
    masked_img = imagetools.inside_outline(cv_img, blue_outline_img)
    shapened_img = imagetools.mix(imagetools.sharpen(masked_img, 1), masked_img, 0.5)
    white_outline_img = imagetools.constant_color_key(
        shapened_img,
        (255, 255, 255),
        (252, 251, 251),
        (248, 227, 159),
        threshold=0.9,
    )
    bg_mask = imagetools.border_flood_fill(white_outline_img)
    fg_mask = 255 - bg_mask
    imagetools.fill_area(fg_mask, (0,), size_lt=100)
    fg_img = cv2.copyTo(masked_img, fg_mask)
    empty_mask = imagetools.constant_color_key(fg_img, (126, 121, 121))
    if os.getenv("DEBUG") == __name__:
        _LOGGER.debug(
            "soul: img=%s",
            imagetools.image_hash(img, save_path=g.image_path),
        )
        cv2.imshow("soul", cv_img)
        cv2.imshow("sharpened", shapened_img)
        cv2.imshow("right_bottom_icon", imagetools.cv_image(right_bottom_icon_img))
        cv2.imshow("blue_outline", blue_outline_img)
        cv2.imshow("white_outline", white_outline_img)
        cv2.imshow("bg_mask", bg_mask)
        cv2.imshow("fg_mask", fg_mask)
        cv2.imshow("empty_mask", empty_mask)
        cv2.waitKey()
        cv2.destroyAllWindows()

    fg_avg = np.average(fg_mask)
    if fg_avg < 100:
        return -1
    empty_avg = np.average(empty_mask)
    outline_avg = 45
    return max(0, min(1, 1 - (empty_avg / (fg_avg - outline_avg))))


class Partner:
    TYPE_SPEED: int = 1
    TYPE_STAMINA: int = 2
    TYPE_POWER: int = 3
    TYPE_GUTS: int = 4
    TYPE_WISDOM: int = 5
    TYPE_FRIEND: int = 6
    TYPE_OTHER: int = 7
    TYPE_TEAMMATE: int = 8

    def __init__(self):
        self.level = 0
        self.type = 0
        self.has_hint = False
        self.has_training = False
        self.has_soul_burst = False
        self.soul = -1
        self.icon_bbox = (0, 0, 0, 0)

    def __str__(self):
        training_text = "No"
        if self.has_training:
            training_text = "Yes"
        if self.has_soul_burst:
            training_text = "Burst"

        return (
            f"Partner<type={self.type_text(self.type)} lv={self.level} "
            f"hint={self.has_hint} training={training_text} soul={self.soul} icon_bbox={self.icon_bbox}>)"
        )

    def score(self, ctx: Context) -> float:
        if self.type == self.TYPE_OTHER:
            return 2 + self.level
        ret = 0
        if 0 <= self.level < 4:
            ret = mathtools.interpolate(
                ctx.turn_count(),
                (
                    (0, 5),
                    (24, 3),
                    (48, 2),
                    (72, 0),
                ),
            )
        if ctx.date[0] < 4:
            if self.has_training and self.soul < 1:
                ret += 7
            if self.has_soul_burst:
                ret += 4
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
            Partner.TYPE_TEAMMATE: "tm",
        }.get(v, f"unknown({v})")

    @classmethod
    def _from_training_scene_icon(
        cls, ctx: Context, img: Image, bbox: Tuple[int, int, int, int]
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

        soul = -1
        if ctx.scenario == ctx.SCENARIO_AOHARU:
            soul = _recognize_soul(rp, img, bbox)

        if level < 0 and soul < 0:
            return None
        self = cls.new()
        self.icon_bbox = bbox
        self.level = level
        self.soul = soul
        self.has_hint = _recognize_has_hint(rp, icon_img)
        self.has_training = _recognize_has_training(ctx, rp, icon_img)
        self.has_soul_burst = _recognize_has_soul_burst(ctx, rp, icon_img)
        if self.has_soul_burst:
            self.has_training = True
            self.soul = 1
        self.type = _recognize_type_color(rp, icon_img)
        if soul >= 0 and self.type == Partner.TYPE_OTHER:
            self.type = Partner.TYPE_TEAMMATE
        _LOGGER.debug("partner: %s", self)
        return self

    @classmethod
    def from_training_scene(cls, img: Image) -> Iterator[Partner]:
        ctx = Context()
        ctx.scenario = ctx.SCENARIO_URA
        return cls.from_training_scene_v2(ctx, img)

    @classmethod
    def from_training_scene_v2(cls, ctx: Context, img: Image) -> Iterator[Partner]:
        rp = mathtools.ResizeProxy(img.width)

        icon_bbox, icon_y_offset = {
            ctx.SCENARIO_URA: (
                rp.vector4((448, 146, 516, 220), 540),
                rp.vector(90, 540),
            ),
            ctx.SCENARIO_AOHARU: (
                rp.vector4((448, 147, 516, 220), 540),
                rp.vector(86, 540),
            ),
        }[ctx.scenario]
        icons_bottom = rp.vector(578, 540)
        while icon_bbox[2] < icons_bottom:
            v = cls._from_training_scene_icon(ctx, img, icon_bbox)
            if not v:
                break
            yield v
            icon_bbox = (
                icon_bbox[0],
                icon_bbox[1] + icon_y_offset,
                icon_bbox[2],
                icon_bbox[3] + icon_y_offset,
            )

    def to_short_text(self):
        ret = self.type_text(self.type)
        if self.level > 0:
            ret += f"@{self.level}"
        if self.has_hint:
            ret += "!"
        if self.has_soul_burst:
            ret += "^^"
        elif self.has_training:
            ret += "^"
        if self.soul >= 0:
            ret += f"({round(self.soul * 100)}%)"
        return ret


g.partner_class = Partner

# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import os
from typing import Iterator, Set, Text, Type

import cv2
from PIL.Image import Image

from .. import imagetools, mathtools, ocr, template, templates, texttools
from .context import Context
from .training import Training


class g:
    option_class: Type[Option]
    names: Set[Text] = set()


def _ocr_name(img: Image) -> Text:
    img = imagetools.resize(img, height=32)
    cv_img = imagetools.cv_image(img.convert("L"))
    _, binary_img = cv2.threshold(cv_img, 120, 255, cv2.THRESH_BINARY_INV)

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    text = ocr.text(imagetools.pil_image(binary_img))
    return texttools.choose(text, g.names)


class Option:
    TYPE_UNDEFINED = 0
    # main character
    TYPE_MAIN = 1
    # support card
    TYPE_SUPPORT = 2

    @classmethod
    def new(cls) -> Option:
        return g.option_class()

    def __init__(self) -> None:
        self.type = Option.TYPE_UNDEFINED
        self.current_event_count = 0
        self.total_event_count = 0
        self.position = (0, 0)
        self.bbox = (0, 0, 0, 0)
        self.name = ""

    def __str__(self) -> Text:
        type_text = {
            Option.TYPE_MAIN: "MAIN",
            Option.TYPE_SUPPORT: "SUPPORT",
            Option.TYPE_UNDEFINED: "UNDEFINED",
        }.get(self.type, "UNKNOWN")
        return f"Option<name={self.name},type={type_text},event={self.current_event_count}/{self.total_event_count},pos={self.position}>"

    def disabled(self, ctx: Context) -> bool:
        if (
            self.total_event_count > 0
            and self.current_event_count >= self.total_event_count
        ):
            return True
        return False

    def heal_rate(self, ctx: Context) -> float:
        if self.type == self.TYPE_MAIN:
            if ctx.CONDITION_HEADACHE in ctx.conditions:
                return 0
            return 0.5
        if self.type == self.TYPE_SUPPORT:
            return 0.4
        return 0

    def mood_rate(self, ctx: Context) -> float:
        if ctx.mood == ctx.MOOD_VERY_GOOD:
            return 0
        if self.type == self.TYPE_MAIN:
            return 1
        if self.type == self.TYPE_SUPPORT:
            return 0.5
        return 0

    def vitality(self, ctx: Context) -> float:
        ret = 5
        if self.type == self.TYPE_SUPPORT:
            ret = 15
        return ret / ctx.max_vitality

    def score(self, ctx: Context) -> float:
        ret = 0

        mood = mathtools.interpolate(
            ctx.turn_count(),
            (
                (0, 25),
                (24, 20),
                (48, 15),
                (72, 10),
            ),
        )
        max_mood_rate = {
            ctx.MOOD_VERY_GOOD: 0,
            ctx.MOOD_GOOD: 1,
            ctx.MOOD_NORMAL: 2,
            ctx.MOOD_BAD: 3,
            ctx.MOOD_VERY_BAD: 4,
        }[ctx.mood]
        ret += mood * min(self.mood_rate(ctx), max_mood_rate)

        heal = (
            len(
                set(
                    (
                        Context.CONDITION_HEADACHE,
                        Context.CONDITION_OVERWEIGHT,
                    )
                ).intersection(ctx.conditions)
            )
            * 20
        )
        ret += heal * self.heal_rate(ctx)

        t = Training.new()
        t.vitality = self.vitality(ctx)
        ret += t.score(ctx)

        # try finish all events
        if self.type == self.TYPE_SUPPORT:
            ret += mathtools.interpolate(
                ctx.turn_count(),
                (
                    (0, 0),
                    (48, 5),
                    (72, 20),
                    (78, 30),
                ),
            )

        return ret

    def update_by_option_image(self, img: Image) -> None:
        if os.getenv("DEBUG") == __name__:
            imagetools.show(img, "option image")

        if self.type == Option.TYPE_SUPPORT:
            rp = mathtools.ResizeProxy(img.width)

            event1_pos = rp.vector2((338 - 18, 353 - 286), 500)
            event2_pos = rp.vector2((375 - 18, 353 - 286), 500)
            event3_pos = rp.vector2((413 - 18, 353 - 286), 500)
            event4_pos = rp.vector2((450 - 18, 353 - 286), 500)
            event5_pos = rp.vector2((489 - 18, 353 - 286), 500)

            self.current_event_count = 0
            self.total_event_count = 5
            for pos in (
                event1_pos,
                event2_pos,
                event3_pos,
                event4_pos,
                event5_pos,
            ):
                is_gray = (
                    imagetools.compare_color(img.getpixel(pos), (231, 227, 225)) > 0.9
                )
                if not is_gray:
                    self.current_event_count += 1

            name_bbox = rp.vector4((95, 16, 316, 38), 540)
            self.name = _ocr_name(img.crop(name_bbox))

    @classmethod
    def from_menu(cls, img: Image) -> Iterator[Option]:
        rp = mathtools.ResizeProxy(img.width)
        for _, pos in template.match(
            img, templates.SINGLE_MODE_GO_OUT_OPTION_LEFT_BORDER
        ):
            x, y = pos
            bbox = (x, y, x + rp.vector(500, 540), y + rp.vector(100, 540))
            friend_ship_gauge_pos = (rp.vector(348, 540), y + rp.vector(23, 540))
            has_friend_ship_gauge = (
                imagetools.compare_color(
                    img.getpixel(friend_ship_gauge_pos), (236, 231, 228)
                )
                > 0.9
            )
            option = cls.new()
            option.position = (x + rp.vector(100, 540), y + rp.vector(46, 540))
            option.bbox = bbox
            if has_friend_ship_gauge:
                option.type = cls.TYPE_SUPPORT
            else:
                option.type = cls.TYPE_MAIN

            option.update_by_option_image(img.crop(bbox))
            yield option


g.option_class = Option

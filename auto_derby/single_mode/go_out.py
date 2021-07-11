# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Iterator, Text, Type

from PIL.Image import Image

from .. import imagetools, mathtools, template, templates
from .context import Context
import os


class g:
    option_class: Type[Option]


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

    def __str__(self) -> Text:
        type_text = {
            Option.TYPE_MAIN: "MAIN",
            Option.TYPE_SUPPORT: "SUPPORT",
            Option.TYPE_UNDEFINED: "UNDEFINED",
        }.get(self.type, "UNKNOWN")
        return f"Option<type={type_text},event={self.current_event_count}/{self.total_event_count},pos={self.position}>"

    def score(self, ctx: Context) -> float:
        ret = 0
        if self.type == Option.TYPE_MAIN:
            ret += (ctx.MOOD_VERY_GOOD[0] - ctx.mood[0]) * 300
        elif self.type == Option.TYPE_SUPPORT:
            ret += 20
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
            if has_friend_ship_gauge:
                option.type = cls.TYPE_SUPPORT
            else:
                option.type = cls.TYPE_MAIN

            option.update_by_option_image(img.crop(bbox))
            yield option


g.option_class = Option

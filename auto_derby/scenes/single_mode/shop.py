# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import os
from typing import Any, Dict, Iterator, Text, Tuple

import cv2
from PIL.Image import Image

from ... import action, imagetools, mathtools, template, templates
from ...single_mode import Context, item
from ...single_mode.item import Item
from ..scene import Scene, SceneHolder
from .command import CommandScene


def _title_image(rp: mathtools.ResizeProxy, item_img: Image) -> Image:
    bbox = rp.vector4((100, 10, 375, 32), 540)
    cv_img = imagetools.cv_image(item_img.crop(bbox))
    binary_img = imagetools.constant_color_key(cv_img, (22, 64, 121))
    binary_img = imagetools.auto_crop(binary_img)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("item_img", imagetools.cv_image(item_img))
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    return imagetools.pil_image(binary_img)


def _recognize_item(rp: mathtools.ResizeProxy, img: Image) -> Item:
    v = item.from_title_image(_title_image(rp, img))

    # TODO: recognize current price
    v.price = v.original_price
    return v


def _recognize_menu(img: Image) -> Iterator[Tuple[Item, Tuple[int, int]]]:
    rp = mathtools.ResizeProxy(img.width)

    for _, pos in sorted(
        template.match(img, templates.EXCHANGE_BUTTON),
        key=lambda x: x[1][1],
    ):
        _, y = pos
        bbox = (
            rp.vector(19, 540),
            y - rp.vector(34, 540),
            rp.vector(521, 540),
            y + rp.vector(68, 540),
        )
        yield _recognize_item(rp, img.crop(bbox)), pos


class ShopScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.items: Tuple[Item, ...] = ()

        # top = 0, bottom = 1
        self._menu_position = 0

    @classmethod
    def name(cls):
        return "single-mode-shop"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        CommandScene.enter(ctx)
        action.wait_tap_image(
            templates.SINGLE_MODE_COMMAND_SHOP,
        )
        return cls()

    def _scroll_page(self, direction: int = 0):
        if direction == 0:
            direction = 1 if self._menu_position < 0.5 else -1

        rp = action.resize_proxy()
        action.swipe(
            rp.vector2((100, 600), 466),
            dy=rp.vector(-50 * direction, 466),
            duration=0.2,
        )
        # prevent inertial scrolling
        action.tap(rp.vector2((15, 600), 540))

    def _on_scroll_to_end(self):
        self._menu_position = 1 - self._menu_position

    def _recognize_items(self, static: bool = False) -> None:
        self.items = ()
        while True:
            new_items = tuple(
                i
                for i, _ in _recognize_menu(template.screenshot())
                if i not in self.items
            )
            if not new_items:
                self._on_scroll_to_end()
                return
            self.items += new_items
            if static:
                break
            self._scroll_page()

    def recognize(self, ctx: Context, *, static: bool = False) -> None:
        self._recognize_items(static)

    def exchange_item(self, item: Item) -> None:
        while True:
            for match, pos in _recognize_menu(template.screenshot()):
                if item == match:
                    action.tap(pos)
                    raise NotImplementedError()
            self._scroll_page()

    def to_dict(self) -> Dict[Text, Any]:
        d: Dict[Text, Any] = {
            "items": [{"id": i.id, "name": i.name} for i in self.items]
        }
        return d

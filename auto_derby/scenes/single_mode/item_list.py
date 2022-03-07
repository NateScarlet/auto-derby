# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterator, Sequence, Text, Tuple

import cv2
from PIL.Image import Image

from ... import action, imagetools, mathtools, template, templates, ocr
from ...single_mode import Context, item
from ...single_mode.item import Item
from ..scene import Scene, SceneHolder
from .command import CommandScene

_LOGGER = logging.getLogger(__name__)


def _title_image(rp: mathtools.ResizeProxy, item_img: Image) -> Image:
    bbox = rp.vector4((100, 10, 407, 32), 540)
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


def _recognize_quantity(rp: mathtools.ResizeProxy, item_img: Image) -> int:
    bbox = rp.vector4((179, 43, 382, 64), 540)
    cv_img = imagetools.cv_image(item_img.crop(bbox))
    binary_img = imagetools.constant_color_key(cv_img, (22, 64, 121))
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("item_img", imagetools.cv_image(item_img))
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text)


def _recognize_disabled(rp: mathtools.ResizeProxy, item_img: Image) -> bool:
    try:
        next(template.match(item_img, templates.SINGLE_MODE_ITEM_LIST_USE_BUTTON))
        return False
    except StopIteration:
        return True


def _recognize_item(rp: mathtools.ResizeProxy, img: Image) -> Item:
    v = item.from_title_image(_title_image(rp, img))
    v.quantity = _recognize_quantity(rp, img)
    v.disabled = _recognize_disabled(rp, img)
    return v


def _recognize_menu(img: Image) -> Iterator[Tuple[Item, Tuple[int, int]]]:
    rp = mathtools.ResizeProxy(img.width)

    min_y = rp.vector(130, 540)
    for _, pos in sorted(
        template.match(img, templates.SINGLE_MODE_ITEM_LIST_CURRENT_QUANTITY),
        key=lambda x: x[1][1],
    ):
        x, y = pos
        if y < min_y:
            # ignore partial visible
            continue
        bbox = (
            rp.vector(22, 540),
            y - rp.vector(52, 540),
            rp.vector(518, 540),
            y + rp.vector(48, 540),
        )
        yield _recognize_item(rp, img.crop(bbox)), (x + rp.vector(303, 540), y)


class ItemListScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.items: Tuple[item.Item, ...] = ()
        # top = 0, bottom = 1
        self._menu_position = 0

    @classmethod
    def name(cls):
        return "single-mode-item-list"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        CommandScene.enter(ctx)
        action.wait_tap_image(
            templates.SINGLE_MODE_ITEM_LIST_BUTTON,
        )
        action.wait_image(templates.CLOSE_BUTTON)
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

    def to_dict(self) -> Dict[Text, Any]:
        d: Dict[Text, Any] = {
            "items": [
                {
                    "id": i.id,
                    "name": i.name,
                    "quantity": i.quantity,
                    "disabled": i.disabled,
                }
                for i in self.items
            ]
        }
        return d

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
        if not self.items:
            _LOGGER.warn("not found items")

    def recognize(self, ctx: Context, *, static: bool = False) -> None:
        self._recognize_items(static)
        ctx.items = self.items
        ctx.items_last_updated_turn = ctx.turn_count()

    def use_items(self, ctx: Context, items: Sequence[Item]) -> None:
        remains = list(items)
        while remains:
            for match, pos in _recognize_menu(template.screenshot()):
                if match not in remains:
                    continue
                _LOGGER.info("use: %s", match)
                action.tap(pos)
                raise NotImplementedError()
                remains.remove(match)
                match.quantity -= 1
            self._scroll_page()
        for i in remains:
            _LOGGER.info("failed to exchange item: %s", i)
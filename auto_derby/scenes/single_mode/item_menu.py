# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterator, Sequence, Text, Tuple

import cv2
from PIL.Image import Image

from ... import action, imagetools, mathtools, ocr, template, templates
from ...single_mode import Context, item
from ...single_mode.item import Item, ItemList
from ..scene import Scene, SceneHolder
from ..vertical_scroll import VerticalScroll
from .command import CommandScene

_LOGGER = logging.getLogger(__name__)


def _title_image(rp: mathtools.ResizeProxy, item_img: Image) -> Image:
    bbox = rp.vector4((100, 10, 383, 32), 540)
    cv_img = imagetools.cv_image(item_img.crop(bbox).convert("L"))
    _, binary_img = cv2.threshold(cv_img, 120, 255, cv2.THRESH_BINARY_INV)
    binary_img = imagetools.auto_crop(binary_img)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("item_img", imagetools.cv_image(item_img))
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    return imagetools.pil_image(binary_img)


def _recognize_quantity(
    rp: mathtools.ResizeProxy, item_img: Image, thresh: float = 160
) -> int:
    bbox = rp.vector4((179, 43, 194, 64), 540)
    cv_img = imagetools.cv_image(
        imagetools.resize(item_img.crop(bbox).convert("L"), height=32)
    )
    _, binary_img = cv2.threshold(cv_img, thresh, 255, cv2.THRESH_BINARY_INV)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("item_img", imagetools.cv_image(item_img))
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text)


def _recognize_item(rp: mathtools.ResizeProxy, img: Image) -> Item:
    v = item.from_name_image(_title_image(rp, img))
    v.quantity = _recognize_quantity(rp, img, 160)
    v.disabled = False
    return v


def _recognize_disabled_item(rp: mathtools.ResizeProxy, img: Image) -> Item:
    v = item.from_name_image(_title_image(rp, img))
    v.quantity = _recognize_quantity(rp, img, 120)
    v.disabled = True
    return v


def _recognize_menu(
    img: Image, min_y: int = 130
) -> Iterator[Tuple[Item, Tuple[int, int]]]:
    rp = mathtools.ResizeProxy(img.width)

    min_y = rp.vector(min_y, 540)
    for tmpl, pos in sorted(
        template.match(
            img,
            templates.SINGLE_MODE_ITEM_MENU_CURRENT_QUANTITY,
            templates.SINGLE_MODE_ITEM_MENU_CURRENT_QUANTITY_DISABLED,
        ),
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
        if tmpl.name == templates.SINGLE_MODE_ITEM_MENU_CURRENT_QUANTITY:
            yield _recognize_item(rp, img.crop(bbox)), (x + rp.vector(360, 540), y)
        else:
            yield _recognize_disabled_item(rp, img.crop(bbox)), (
                x + rp.vector(360, 540),
                y,
            )


class ItemMenuScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.items = item.ItemList()
        rp = action.resize_proxy()
        self._scroll = VerticalScroll(
            origin=rp.vector2((17, 540), 540),
            page_size=150,
            max_page=5,
        )

    @classmethod
    def name(cls):
        return "single-mode-item-menu"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        CommandScene.enter(ctx)
        action.wait_tap_image(
            templates.SINGLE_MODE_ITEM_MENU_BUTTON,
        )
        action.wait_image_stable(templates.CLOSE_BUTTON)
        return cls()

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
        self.items = ItemList()
        while self._scroll.next():
            new_items = tuple(
                i
                for i, _ in _recognize_menu(template.screenshot())
                if i not in self.items
            )
            if not new_items:
                self._scroll.on_end()
                self._scroll.complete()
                return
            for i in new_items:
                _LOGGER.debug("found: %s", i)
            self.items.update(*new_items)
            if static:
                break
        if not self.items:
            _LOGGER.warning("not found any item")

    def recognize(self, ctx: Context, *, static: bool = False) -> None:
        self._recognize_items(static)
        ctx.items = self.items
        ctx.items_last_updated_turn = ctx.turn_count()

    def use_items(self, ctx: Context, items: Sequence[Item]) -> None:
        remains = list(items)
        in_shop = ctx.scene.name() == "single-mode-shop"

        def _use_visible_items() -> None:
            for match, pos in _recognize_menu(
                template.screenshot(), 130 if not in_shop else 194
            ):
                if match not in remains:
                    continue
                if match.disabled:
                    _LOGGER.warning("skip disabled: %s", match)
                    remains.remove(match)
                    continue
                item = next(i for i in items if i == match)
                _LOGGER.info("use: %s", match)
                remains.remove(match)
                for _ in range(item.quantity):
                    action.tap(pos)
                    ctx.items.remove(match.id, 1)
                ctx.item_history.append(ctx, match)
                return _use_visible_items()

        while self._scroll.next():
            for i in remains:
                _LOGGER.debug("use remain: %s", i)
            _use_visible_items()
            if not remains:
                break
        self._scroll.complete()
        for i in remains:
            _LOGGER.warning("use remain: %s", i)
        tmpl, _ = action.wait_image(
            templates.SINGLE_MODE_SHOP_USE_CONFIRM_BUTTON,
            templates.CLOSE_BUTTON,
        )
        if tmpl.name == templates.SINGLE_MODE_SHOP_USE_CONFIRM_BUTTON:
            action.wait_tap_image(templates.SINGLE_MODE_SHOP_USE_CONFIRM_BUTTON)
            action.wait_tap_image(templates.SINGLE_MODE_ITEM_USE_BUTTON)
        if not in_shop:
            action.wait_image_stable(templates.CLOSE_BUTTON)

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
from ...single_mode.item import Item
from ..scene import Scene, SceneHolder
from ..vertical_scroll import VerticalScroll
from .command import CommandScene
from .shop_exchanged_item_menu import ShopExchangedItemMenuScene

_LOGGER = logging.getLogger(__name__)


def _title_image(rp: mathtools.ResizeProxy, item_img: Image) -> Image:
    bbox = rp.vector4((100, 10, 375, 32), 540)
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


def _recognize_price(rp: mathtools.ResizeProxy, item_img: Image) -> int:
    bbox = rp.vector4((185, 41, 389, 64), 540)
    price_img = imagetools.resize(item_img.crop(bbox), height=32)
    pink_mask = imagetools.constant_color_key(
        imagetools.cv_image(price_img),
        (118, 51, 255),
    )
    pink_x, _, pink_w, _ = cv2.boundingRect(cv2.findNonZero(pink_mask))
    has_discount = pink_w > 80
    if has_discount:
        binary_img = pink_mask[:, round(pink_x + pink_w * 0.6) :]
    else:
        cv_img = 255 - imagetools.cv_image(price_img.convert("L"))
        _, binary_img = cv2.threshold(cv_img, 120, 255, cv2.THRESH_BINARY)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("item_img", imagetools.cv_image(item_img))
        cv2.imshow("pink_mask", pink_mask)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text)


def _recognize_item(rp: mathtools.ResizeProxy, img: Image) -> Item:
    v = item.from_name_image(_title_image(rp, img))
    v.price = _recognize_price(rp, img)
    return v


def _recognize_menu(img: Image) -> Iterator[Tuple[Item, Tuple[int, int]]]:
    rp = mathtools.ResizeProxy(img.width)

    y_min = rp.vector(390, 540)
    y_max = rp.vector(700, 540)
    for _, pos in sorted(
        template.match(img, templates.SINGLE_MODE_SHOP_ITEM_PRICE),
        key=lambda x: x[1][1],
    ):
        _, y = pos
        if not (y_min < y < y_max):
            # ignore partial visible
            continue
        bbox = (
            rp.vector(19, 540),
            y - rp.vector(49, 540),
            rp.vector(521, 540),
            y + rp.vector(53, 540),
        )
        yield _recognize_item(rp, img.crop(bbox)), (
            rp.vector(450, 540),
            y - rp.vector(15, 540),
        )


class ShopScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.items: Tuple[Item, ...] = ()

        rp = action.resize_proxy()
        self._scroll = VerticalScroll(
            origin=rp.vector2((17, 540), 540),
            page_size=150,
            max_page=10,
        )

    @classmethod
    def name(cls):
        return "single-mode-shop"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        if ctx.scene.name() == "single-mode-shop-exchanged-item-menu":
            action.tap_image(templates.CLOSE_BUTTON)
        else:
            CommandScene.enter(ctx)
            action.wait_tap_image(
                templates.SINGLE_MODE_COMMAND_SHOP,
            )
        action.wait_image(templates.RETURN_BUTTON)
        return cls()

    def _recognize_items(self, static: bool = False) -> None:
        self.items = ()
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
            self.items += new_items
            if static:
                break
        if not self.items:
            _LOGGER.warning("not found any items")

    def recognize(self, ctx: Context, *, static: bool = False) -> None:
        self._recognize_items(static)

    def exchange_items(self, ctx: Context, items: Sequence[Item]) -> None:
        remains = list(items)
        selected: Sequence[Item] = list()

        def _select_visible_items() -> None:
            for match, pos in _recognize_menu(template.screenshot()):
                if match not in remains:
                    continue
                if ctx.items.get(match.id).quantity >= match.max_quantity:
                    remains.remove(match)
                    _LOGGER.warning("skip due to max quantity: %s", match)
                    continue

                _LOGGER.info("exchange: %s", match)
                action.tap(pos)
                ctx.shop_coin -= match.price
                remains.remove(match)
                selected.append(match)
                return _select_visible_items()

        while self._scroll.next():
            for i in remains:
                _LOGGER.debug("exchange remain: %s", i)
            _select_visible_items()
            if not remains:
                break
        self._scroll.complete()
        for i in remains:
            _LOGGER.warning("exchange remain: %s", i)

        if selected:
            action.wait_tap_image(templates.SINGLE_MODE_SHOP_DECIDE_BUTTON)
            for i in selected:
                ctx.items.put(i.id, 1)
            scene = ShopExchangedItemMenuScene.enter(ctx)
            would_use = [i for i in selected if i.should_use_directly(ctx)]
            scene.use_items(ctx, would_use)
            self.enter(ctx)

    def to_dict(self) -> Dict[Text, Any]:
        d: Dict[Text, Any] = {
            "items": [
                {"id": i.id, "name": i.name, "price": i.price} for i in self.items
            ]
        }
        return d

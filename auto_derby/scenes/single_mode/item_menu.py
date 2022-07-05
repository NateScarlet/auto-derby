# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import traceback
from collections import defaultdict
from typing import Any, DefaultDict, Dict, Iterator, Sequence, Text, Tuple

import cv2
from PIL.Image import Image

from ... import action, app, imagetools, mathtools, ocr, template, templates
from ...single_mode import Context, item
from ...single_mode.item import Item, ItemList
from ..scene import Scene, SceneHolder
from ..vertical_scroll import VerticalScroll
from .command import CommandScene


def _title_image(rp: mathtools.ResizeProxy, item_img: Image, disabled: bool) -> Image:
    bbox = rp.vector4((100, 10, 383, 32), 540)
    cv_img = imagetools.cv_image(item_img.crop(bbox).convert("L"))
    _, binary_img = cv2.threshold(
        cv_img,
        80 if disabled else 120,
        255,
        cv2.THRESH_BINARY_INV,
    )
    binary_img = imagetools.auto_crop(binary_img)

    app.log.image(
        "title image",
        cv_img,
        layers={"binary": binary_img},
        level=app.DEBUG,
    )
    return imagetools.pil_image(binary_img)


def _recognize_quantity(
    rp: mathtools.ResizeProxy, item_img: Image, disabled: bool
) -> int:
    bbox = rp.vector4((179, 43, 194, 64), 540)
    cv_img = imagetools.cv_image(
        imagetools.resize(item_img.crop(bbox).convert("L"), height=32)
    )
    _, binary_img = cv2.threshold(
        cv_img, 120 if disabled else 160, 255, cv2.THRESH_BINARY_INV
    )
    app.log.image(
        "recognize quantity",
        cv_img,
        layers={"binary": binary_img},
        level=app.DEBUG,
    )
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text)


def _recognize_item(rp: mathtools.ResizeProxy, img: Image, disabled: bool) -> Item:
    try:
        v = item.from_name_image(_title_image(rp, img, disabled))
        v.quantity = _recognize_quantity(rp, img, disabled)
        v.disabled = disabled
        app.log.image(("recognize: %s" % v), img, level=app.DEBUG)
        return v
    except:
        app.log.image(
            ("recognition failed: %s" % traceback.format_exc()), img, level=app.ERROR
        )
        raise


def _recognize_menu(img: Image, min_y: int) -> Iterator[Tuple[Item, app.Rect]]:
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
        disabled = tmpl.name != templates.SINGLE_MODE_ITEM_MENU_CURRENT_QUANTITY
        yield _recognize_item(rp, img.crop(bbox), disabled), (
            x + rp.vector(360, 540),
            y,
            rp.vector(10, 540),
            rp.vector(10, 540),
        )


class ItemMenuScene(Scene):
    _item_min_y = 130

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
    def name(cls) -> Text:
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
                for i, _ in _recognize_menu(app.device.screenshot(), self._item_min_y)
                if i not in self.items
            )
            if not new_items:
                self._scroll.on_end()
                self._scroll.complete()
                return
            self.items.update(*new_items)
            if static:
                break
        if not self.items:
            app.log.text("not found any item", level=app.WARN)

    def recognize(self, ctx: Context, *, static: bool = False) -> None:
        self._recognize_items(static)
        ctx.items = self.items
        ctx.items_last_updated_turn = ctx.turn_count()

    def _after_use_confirm(self, ctx: Context):
        # wait menu disappear animation
        action.wait_image_stable(templates.CLOSE_BUTTON)

    def use_items(self, ctx: Context, items: Sequence[Item]) -> None:
        if not items:
            return

        remains: DefaultDict[int, int] = defaultdict(lambda: 0)
        for i in items:
            remains[i.id] += i.quantity or 1
        selected: Sequence[Item] = []

        def _select_visible_items() -> None:
            for match, button_rect in _recognize_menu(
                app.device.screenshot(), self._item_min_y
            ):
                if match.id not in remains:
                    continue
                if match.disabled:
                    if match.auto_used():
                        ctx.items.remove(match.id, remains[match.id])
                        for _ in range(remains[match.id]):
                            ctx.item_history.append(ctx, match)

                    app.log.text("skip disabled: %s" % match, level=app.WARN)
                    del remains[match.id]
                    continue
                app.log.text("select: %s" % match)
                while remains[match.id]:
                    app.device.tap(button_rect)
                    remains[match.id] -= 1
                    selected.append(match)
                del remains[match.id]
                return _select_visible_items()

        while self._scroll.next():
            for k, v in remains.items():
                i = item.get(k)
                i.quantity = v
                app.log.text("use remain: %s" % i, level=app.DEBUG)
            _select_visible_items()
            if not remains:
                break
        self._scroll.complete()

        if selected:
            action.wait_tap_image(templates.SINGLE_MODE_SHOP_USE_CONFIRM_BUTTON)
            action.wait_tap_image(templates.SINGLE_MODE_ITEM_USE_BUTTON)
            self._after_use_confirm(ctx)
            for i in selected:
                ctx.items.remove(i.id, 1)
                ctx.item_history.append(ctx, i)

        for i in remains:
            app.log.text("use remain: %s" % item.get(i), level=app.WARN)

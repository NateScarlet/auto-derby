# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Text

from ... import action, templates
from ...single_mode.context import Context
from ..scene import Scene, SceneHolder
from .item_menu import ItemMenuScene


class ShopExchangedItemMenuScene(ItemMenuScene):
    _item_min_y = 194

    @classmethod
    def name(cls) -> Text:
        return "single-mode-shop-exchanged-item-menu"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        # wait animation
        action.wait_image_stable(templates.CLOSE_BUTTON)
        return cls()

    def _after_use_confirm(self, ctx: Context):
        from .shop import ShopScene

        ShopScene.enter(ctx)

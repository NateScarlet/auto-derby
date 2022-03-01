# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ..scene import Scene, SceneHolder


from .command import CommandScene
from ... import action, templates


class ShopScene(Scene):
    def __init__(self) -> None:
        super().__init__()

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

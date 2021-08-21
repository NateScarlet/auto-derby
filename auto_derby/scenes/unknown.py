# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from .scene import Scene, SceneHolder


class UnknownScene(Scene):
    @classmethod
    def name(cls):
        return "unknown"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        return cls()

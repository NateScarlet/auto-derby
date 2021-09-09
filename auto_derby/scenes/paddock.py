# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import time

from .. import action, templates
from .scene import Scene, SceneHolder
from ..constants import RuningStyle


class PaddockScene(Scene):
    @classmethod
    def name(cls):
        return "paddock"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        action.wait_image(templates.RACE_RUNNING_STYLE_CHANGE_BUTTON)
        return cls()

    def choose_runing_style(self, style: RuningStyle):
        rp = action.resize_proxy()
        button_pos = {
            RuningStyle.LEAD: rp.vector2((360, 500), 466),
            RuningStyle.HEAD: rp.vector2((260, 500), 466),
            RuningStyle.MIDDLE: rp.vector2((160, 500), 466),
            RuningStyle.LAST: rp.vector2((60, 500), 466),
        }[style]
        action.wait_tap_image(templates.RACE_RUNNING_STYLE_CHANGE_BUTTON)
        _, pos = action.wait_image(templates.RACE_CONFIRM_BUTTON)
        time.sleep(0.5)
        action.tap(button_pos)
        action.tap(pos)

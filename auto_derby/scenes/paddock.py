# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import time

from .. import action, templates, app
from .scene import Scene, SceneHolder
from ..constants import RunningStyle


class PaddockScene(Scene):
    @classmethod
    def name(cls):
        return "paddock"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        action.wait_image(templates.RACE_RUNNING_STYLE_CHANGE_BUTTON)
        return cls()

    def choose_running_style(self, style: RunningStyle):
        rp = action.resize_proxy()
        button_pos = {
            RunningStyle.LEAD: rp.vector2((360, 500), 466),
            RunningStyle.HEAD: rp.vector2((260, 500), 466),
            RunningStyle.MIDDLE: rp.vector2((160, 500), 466),
            RunningStyle.LAST: rp.vector2((60, 500), 466),
        }[style]
        action.wait_tap_image(templates.RACE_RUNNING_STYLE_CHANGE_BUTTON)
        _, pos = action.wait_image(templates.RACE_CONFIRM_BUTTON)
        time.sleep(0.5)
        app.device.tap((*button_pos, 20, 20))
        app.device.tap((*pos, 100, 20))


# deprecated members:
# spell-checker: disable
PaddockScene.choose_runing_style = PaddockScene.choose_running_style  # type: ignore

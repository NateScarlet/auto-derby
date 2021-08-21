# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import time

from .. import action, single_mode, template, templates
from .scene import Scene, SceneHolder


class SingleModeCommandScene(Scene):
    @classmethod
    def name(cls):
        return "single-mode-command"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        if ctx.scene.name() == "single-mode-training":
            action.tap_image(templates.RETURN_BUTTON)
        action.wait_image(
            templates.SINGLE_MODE_COMMAND_TRAINING,
            templates.SINGLE_MODE_FORMAL_RACE_BANNER,
            templates.SINGLE_MODE_URA_FINALS,
        )
        return cls()

    def recognize_class(self, ctx: single_mode.Context):
        action.wait_tap_image(templates.SINGLE_MODE_CLASS_DETAIL_BUTTON)
        time.sleep(0.2)  # wait animation
        action.wait_image(templates.SINGLE_MODE_CLASS_DETAIL_TITLE)
        ctx.update_by_class_detail(template.screenshot())
        action.wait_tap_image(templates.CLOSE_BUTTON)

    def recognize_status(self, ctx: single_mode.Context):
        action.wait_tap_image(templates.SINGLE_MODE_CHARACTER_DETAIL_BUTTON)
        time.sleep(0.2)  # wait animation
        action.wait_image(templates.SINGLE_MODE_CHARACTER_DETAIL_TITLE)
        ctx.update_by_character_detail(template.screenshot())
        action.wait_tap_image(templates.CLOSE_BUTTON)

    def recognize(self, ctx: single_mode.Context):
        action.reset_client_size()
        ctx.update_by_command_scene(template.screenshot(max_age=0))
        if not ctx.fan_count:
            self.recognize_class(ctx)
        if ctx.turf == ctx.STATUS_NONE or ctx.date[1:] == (4, 1):
            self.recognize_status(ctx)

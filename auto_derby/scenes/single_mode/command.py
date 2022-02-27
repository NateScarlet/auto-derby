# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import time
from typing import Any, Dict, Text

from ... import action, single_mode, template, templates, ocr, terminal
from ...scenes import Scene
from ..scene import Scene, SceneHolder


class CommandScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.has_health_care = False
        self.has_scheduled_race = False
        self.can_go_out_with_friend = False
        self.has_shop = False

    @classmethod
    def name(cls):
        return "single-mode-command"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        if ctx.scene.name() == "single-mode-training":
            action.tap_image(templates.RETURN_BUTTON)

        while True:
            tmpl, pos = action.wait_image(
                templates.SINGLE_MODE_COMMAND_TRAINING,
                templates.SINGLE_MODE_FORMAL_RACE_BANNER,
                templates.SINGLE_MODE_URA_FINALS,
                templates.CANCEL_BUTTON,
            )
            if tmpl.name == templates.CANCEL_BUTTON:
                action.tap(pos)
            else:
                break

        return cls()

    def to_dict(self) -> Dict[Text, Any]:
        return {
            "hasHealthCare": self.has_health_care,
            "hasScheduledRace": self.has_scheduled_race,
            "canGoOutWithFriend": self.can_go_out_with_friend,
            "hasShop": self.has_shop,
        }

    def recognize_class(self, ctx: single_mode.Context):
        action.wait_tap_image(
            {
                ctx.SCENARIO_AOHARU: templates.SINGLE_MODE_AOHARU_CLASS_DETAIL_BUTTON,
                ctx.SCENARIO_CLIMAX: templates.SINGLE_MODE_CLIMAX_CLASS_DETAIL_BUTTON,
            }.get(
                ctx.scenario,
                templates.SINGLE_MODE_CLASS_DETAIL_BUTTON,
            )
        )
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

    def recognize_commands(self, ctx: single_mode.Context) -> None:
        self.has_health_care = (
            action.count_image(templates.SINGLE_MODE_COMMAND_HEALTH_CARE) > 0
        )
        self.has_scheduled_race = (
            action.count_image(templates.SINGLE_MODE_SCHEDULED_RACE_OPENING_BANNER) > 0
        )
        self.can_go_out_with_friend = (
            action.count_image(templates.SINGLE_MODE_GO_OUT_FRIEND_ICON) > 0
        )
        if ctx.scenario == ctx.SCENARIO_CLIMAX:
            self.has_shop = action.count_image(templates.SINGLE_MODE_COMMAND_SHOP) > 0

    def recognize_go_out_options(self, ctx: single_mode.Context) -> None:
        if not self.can_go_out_with_friend:
            return

        action.wait_tap_image(single_mode.go_out.command_template(ctx))
        time.sleep(0.5)
        if action.count_image(templates.SINGLE_MODE_GO_OUT_MENU_TITLE):
            ctx.go_out_options = tuple(
                single_mode.go_out.Option.from_menu(template.screenshot(max_age=0))
            )
            action.wait_tap_image(templates.CANCEL_BUTTON)

    def recognize(self, ctx: single_mode.Context):
        action.reset_client_size()
        # animation may not finished
        # https://github.com/NateScarlet/auto-derby/issues/201
        class local:
            next_retry_count = 0

        max_retry = 10

        def _update_with_retry():
            local.next_retry_count += 1
            if local.next_retry_count > max_retry:
                ctx.update_by_command_scene(template.screenshot())
            else:
                with ocr.prompt_disabled(False), terminal.prompt_disabled(True):
                    ctx.update_by_command_scene(template.screenshot())

        action.run_with_retry(
            _update_with_retry,
            max_retry,
        )
        self.recognize_commands(ctx)
        if not ctx.fan_count:
            self.recognize_class(ctx)
        if ctx.turf == ctx.STATUS_NONE or ctx.date[1:] == (4, 1):
            self.recognize_status(ctx)
        if not ctx.go_out_options:
            self.recognize_go_out_options(ctx)
        if self.has_shop:
            # TODO: recognize shop coin count
            pass

# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import os
import time
from typing import Any, Dict, Text

import cv2
import numpy as np
from auto_derby.single_mode.context import Context

from ... import action, imagetools, ocr, single_mode, template, templates, terminal
from ...scenes import Scene
from ..scene import Scene, SceneHolder


def _recognize_climax_grade_point(ctx: Context):
    if ctx.date[0] == 4:
        # in year 4, grade points are replaced by rank points
        ctx.grade_point = 0
        return
    rp = action.resize_proxy()
    bbox = rp.vector4((10, 185, 111, 218), 540)
    img = template.screenshot().crop(bbox)
    x, _ = next(
        template.match(
            img,
            template.Specification(
                templates.SINGLE_MODE_CLIMAX_GRADE_POINT_PT_TEXT,
                threshold=0.8,
            ),
        )
    )[1]
    img = img.crop((0, 0, x, img.height))
    img = imagetools.resize(img, height=32)
    cv_img = imagetools.cv_image(img.convert("L"))
    _, binary_img = cv2.threshold(
        255 - cv_img,
        0,
        255,
        type=cv2.THRESH_OTSU,
    )

    if os.getenv("DEBUG") == __name__ + "[grade_point]":
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(binary_img))
    ctx.grade_point = int(text.rstrip("pt").replace(",", ""))


def _recognize_shop_coin(ctx: Context):
    rp = action.resize_proxy()
    bbox = rp.vector4((305, 881, 371, 896), 540)
    img = template.screenshot().crop(bbox)
    img = imagetools.resize(img, height=32)
    cv_img = np.asarray(img.convert("L"))
    _, binary_img = cv2.threshold(cv_img, 100, 255, cv2.THRESH_BINARY_INV)
    if os.getenv("DEBUG") == __name__ + "[shop_coin]":
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(binary_img))
    ctx.shop_coin = int(text.replace(",", ""))


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
        name = ctx.scene.name()
        if name == "single-mode-training":
            action.wait_tap_image(templates.RETURN_BUTTON)
        if name == "single-mode-shop":
            action.wait_tap_image(templates.RETURN_BUTTON)
        if name == "single-mode-item-list":
            action.wait_tap_image(templates.CLOSE_BUTTON)

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

    def recognize(self, ctx: single_mode.Context, *, static: bool = False):
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
        if not static:
            if not ctx.fan_count:
                self.recognize_class(ctx)
            if ctx.turf == ctx.STATUS_NONE or ctx.date[1:] == (4, 1):
                self.recognize_status(ctx)
            if not ctx.go_out_options:
                self.recognize_go_out_options(ctx)
        if self.has_shop:
            _recognize_shop_coin(ctx)
        if ctx.scenario == ctx.SCENARIO_CLIMAX:
            _recognize_climax_grade_point(ctx)

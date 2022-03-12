# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import time

from ... import action, single_mode, template, templates
from ...single_mode.race import Race, find_by_race_menu_image
from ..scene import Scene, SceneHolder
from ..vertical_scroll import VerticalScroll
from .command import CommandScene


class RaceTurnsIncorrect(ValueError):
    def __init__(self) -> None:
        super().__init__("race turns incorrect")


class RaceMenuScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        rp = action.resize_proxy()
        self._scroll = VerticalScroll(
            origin=rp.vector2((15, 600), 540),
            page_size=50,
            max_page=10,
        )

    @classmethod
    def name(cls):
        return "single-mode-race-menu"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        CommandScene.enter(ctx)
        tmpl, pos = action.wait_image(
            templates.SINGLE_MODE_COMMAND_RACE,
            templates.SINGLE_MODE_FORMAL_RACE_BANNER,
            templates.SINGLE_MODE_URA_FINALS,
            templates.SINGLE_MODE_SCHEDULED_RACE_OPENING_BANNER,
        )
        x, y = pos
        rp = action.resize_proxy()
        if tmpl.name == templates.SINGLE_MODE_FORMAL_RACE_BANNER:
            y += rp.vector(60, 540)
        action.tap((x, y))
        if tmpl.name == templates.SINGLE_MODE_SCHEDULED_RACE_OPENING_BANNER:
            action.wait_tap_image(templates.SINGLE_MODE_GO_TO_SCHEDULED_RACE_BUTTON)
        tmpl, _ = action.wait_image(
            templates.SINGLE_MODE_RACE_START_BUTTON,
            templates.SINGLE_MODE_CONTINUOUS_RACE_TITLE,
        )
        if tmpl.name == templates.SINGLE_MODE_CONTINUOUS_RACE_TITLE:
            if isinstance(ctx, single_mode.Context) and ctx.continuous_race_count() < 3:
                ctx.race_turns.update(range(ctx.turn_count() - 3, ctx.turn_count()))
                action.wait_tap_image(templates.CANCEL_BUTTON)
                raise RaceTurnsIncorrect()
            action.wait_tap_image(templates.GREEN_OK_BUTTON)
        action.wait_image(templates.SINGLE_MODE_RACE_MENU_FAN_ICON)
        return cls()

    def first_race(self, ctx: single_mode.Context) -> Race:
        return next(find_by_race_menu_image(ctx, template.screenshot()))[0]

    def choose_race(self, ctx: single_mode.Context, race: Race) -> None:
        time.sleep(0.2)  # wait animation
        while self._scroll.next():
            for race2, pos in find_by_race_menu_image(ctx, template.screenshot()):
                if race2 == race:
                    action.tap(pos)
                    return
        raise ValueError("not found: %s" % race)

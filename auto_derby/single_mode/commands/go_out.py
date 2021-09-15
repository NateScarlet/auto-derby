# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import time
from typing import Optional, Text

from ... import action, templates, template
from ...scenes.single_mode.command import CommandScene
from .. import Context, go_out
from .command import Command
from .globals import g


def _main_option() -> go_out.Option:
    ret = go_out.Option.new()
    ret.type = ret.TYPE_MAIN
    return ret


class GoOutCommand(Command):
    def __init__(self, option: Optional[go_out.Option] = None) -> None:
        super().__init__()
        self.option = option or _main_option()

    def name(self) -> Text:
        o = self.option
        if o.type == o.TYPE_MAIN:
            return "GoOut<main>"
        if o.type == o.TYPE_SUPPORT:
            return f"GoOut<support:{o.name or o.position}:{o.current_event_count}/{o.total_event_count}>"
        return f"GoOut<{o}>"

    def execute(self, ctx: Context) -> None:
        g.on_command(ctx, self)
        CommandScene.enter(ctx)
        action.tap_image(
            templates.SINGLE_MODE_COMMAND_GO_OUT,
        )
        time.sleep(0.5)
        if action.count_image(templates.SINGLE_MODE_GO_OUT_MENU_TITLE):
            if (
                self.option.position == (0, 0)
                and self.option.type == go_out.Option.TYPE_MAIN
            ):
                self.option = next(
                    i
                    for i in go_out.Option.from_menu(template.screenshot())
                    if i.type == self.option.type
                )
            action.tap(self.option.position)
        if self.option.total_event_count > 0:
            self.option.current_event_count += 1
        return

    def score(self, ctx: Context) -> float:
        return self.option.score(ctx)

# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import Iterator, Set, Text, Tuple, Type, Union

from PIL.Image import Image

from .. import mathtools, template, templates
from .context import Context
from .training import Training


class g:
    option_class: Type[Option]
    names: Set[Text] = set()


def command_template(ctx: Context) -> Union[Text, template.Specification]:
    if ctx.scenario == ctx.SCENARIO_CLIMAX:
        return templates.SINGLE_MODE_CLIMAX_COMMAND_GO_OUT
    return templates.SINGLE_MODE_COMMAND_GO_OUT


class Option:
    TYPE_UNDEFINED = 0
    # main character
    TYPE_MAIN = 1
    # support card
    TYPE_SUPPORT = 2

    @classmethod
    def new(cls) -> Option:
        return g.option_class()

    def __init__(self) -> None:
        self.type: int = Option.TYPE_UNDEFINED
        self.current_event_count = 0
        self.total_event_count = 0
        self.position: Tuple[int, int] = (0, 0)
        self.bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)
        self.name = ""

    def __str__(self) -> Text:
        type_text = {
            Option.TYPE_MAIN: "MAIN",
            Option.TYPE_SUPPORT: "SUPPORT",
            Option.TYPE_UNDEFINED: "UNDEFINED",
        }.get(self.type, "UNKNOWN")
        return f"Option<name={self.name},type={type_text},event={self.current_event_count}/{self.total_event_count},pos={self.position}>"

    def disabled(self, ctx: Context) -> bool:
        if (
            self.total_event_count > 0
            and self.current_event_count >= self.total_event_count
        ):
            return True
        return False

    def heal_rate(self, ctx: Context) -> float:
        if self.type == self.TYPE_MAIN:
            if ctx.CONDITION_HEADACHE in ctx.conditions:
                return 0
            return 0.5
        if self.type == self.TYPE_SUPPORT:
            return 0.4
        return 0

    def mood_rate(self, ctx: Context) -> float:
        if self.type == self.TYPE_MAIN:
            return 1.2
        if self.type == self.TYPE_SUPPORT:
            return 0.5
        return 0

    def vitality(self, ctx: Context) -> float:
        ret = 5
        if self.type == self.TYPE_SUPPORT:
            ret = 15
        return ret / ctx.max_vitality

    def score(self, ctx: Context) -> float:
        ret = 0

        mood = mathtools.interpolate(
            ctx.speed,
            (
                (0, 30),
                (600, 25),
                (900, 20),
                (1200, 15),
            ),
        )
        max_mood_rate = {
            ctx.MOOD_VERY_GOOD: 0,
            ctx.MOOD_GOOD: 1,
            ctx.MOOD_NORMAL: 2,
            ctx.MOOD_BAD: 3,
            ctx.MOOD_VERY_BAD: 4,
        }[ctx.mood]
        ret += mood * min(self.mood_rate(ctx), max_mood_rate)

        heal = (
            len(
                set(
                    (
                        Context.CONDITION_HEADACHE,
                        Context.CONDITION_OVERWEIGHT,
                    )
                ).intersection(ctx.conditions)
            )
            * 20
        )
        ret += heal * self.heal_rate(ctx)

        t = Training.new()
        t.vitality = self.vitality(ctx)
        ret += t.score(ctx)

        # try finish all events
        if self.type == self.TYPE_SUPPORT:
            ret += mathtools.interpolate(
                ctx.turn_count(),
                (
                    (0, 0),
                    (48, 5),
                    (72, 20),
                    (78, 30),
                ),
            )

        return ret

    def update_by_option_image(self, img: Image) -> None:
        import warnings

        warnings.warn(
            "use GoOutMenuScene.recognize instead",
            DeprecationWarning,
        )
        from ..scenes.single_mode.go_out_menu import _recognize_item  # type: ignore

        v = _recognize_item(mathtools.ResizeProxy(int(img.width / 500 * 540)), img)
        self.type = v.type
        self.current_event_count = v.current_event_count
        self.total_event_count = v.total_event_count
        self.position = v.position
        self.bbox = v.bbox
        self.name = v.name

    @classmethod
    def from_menu(cls, img: Image) -> Iterator[Option]:
        import warnings

        warnings.warn(
            "use GoOutMenuScene.recognize instead",
            DeprecationWarning,
        )
        from ..scenes.single_mode.go_out_menu import _recognize_menu  # type: ignore

        return _recognize_menu(img)


g.option_class = Option

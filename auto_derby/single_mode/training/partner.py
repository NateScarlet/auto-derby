# -*- coding=UTF-8 -*-
# pyright: strict
from __future__ import annotations

from typing import Iterator, Text, Tuple

from PIL.Image import Image

from ... import mathtools
from ..context import Context
from .globals import g


class Partner:
    TYPE_SPEED: int = 1
    TYPE_STAMINA: int = 2
    TYPE_POWER: int = 3
    TYPE_GUTS: int = 4
    TYPE_WISDOM: int = 5
    TYPE_FRIEND: int = 6
    TYPE_OTHER: int = 7
    TYPE_TEAMMATE: int = 8

    def __init__(self):
        self.level = 0
        self.type = 0
        self.has_hint = False
        self.has_training = False
        self.has_soul_burst = False
        self.soul: float = -1.0
        self.icon_bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)

    def __str__(self):
        training_text = "No"
        if self.has_training:
            training_text = "Yes"
        if self.has_soul_burst:
            training_text = "Burst"

        return (
            f"Partner<type={self.type_text(self.type)} lv={self.level} "
            f"hint={self.has_hint} training={training_text} soul={self.soul} icon_bbox={self.icon_bbox}>)"
        )

    def score(self, ctx: Context) -> float:
        if self.type == self.TYPE_OTHER:
            return 2 + self.level
        ret = 0
        if 0 <= self.level < 4:
            ret = mathtools.interpolate(
                ctx.turn_count(),
                (
                    (0, 5),
                    (24, 3),
                    (48, 2),
                    (72, 0),
                ),
            )
        if ctx.date[0] < 4:
            if self.has_training and self.soul < 1:
                ret += 7
            if self.has_soul_burst:
                ret += 4
        return ret

    @staticmethod
    def new() -> Partner:
        return g.partner_class()

    @staticmethod
    def type_text(v: int) -> Text:
        return {
            Partner.TYPE_SPEED: "spd",
            Partner.TYPE_STAMINA: "sta",
            Partner.TYPE_POWER: "pow",
            Partner.TYPE_GUTS: "gut",
            Partner.TYPE_WISDOM: "wis",
            Partner.TYPE_FRIEND: "frd",
            Partner.TYPE_OTHER: "oth",
            Partner.TYPE_TEAMMATE: "tm",
        }.get(v, f"unknown({v})")

    def to_short_text(self):
        ret = self.type_text(self.type)
        if self.level > 0:
            ret += f"@{self.level}"
        if self.has_hint:
            ret += "!"
        if self.has_soul_burst:
            ret += "^^"
        elif self.has_training:
            ret += "^"
        if self.soul >= 0:
            ret += f"({round(self.soul * 100)}%)"
        return ret

    @classmethod
    def from_training_scene(cls, img: Image) -> Iterator[Partner]:
        # TODO: remove deprecated method at next major version
        import warnings

        warnings.warn(
            "use from_training_scene_v2 instead",
            DeprecationWarning,
        )
        ctx = Context()
        ctx.scenario = ctx.SCENARIO_URA
        return cls.from_training_scene_v2(ctx, img)

    @classmethod
    def from_training_scene_v2(cls, ctx: Context, img: Image) -> Iterator[Partner]:
        # TODO: remove deprecated method at next major version
        import warnings

        warnings.warn(
            "use TrainingScene.recognize instead",
            DeprecationWarning,
        )
        from ...scenes.single_mode.training import _recognize_partners  # type: ignore

        yield from _recognize_partners(ctx, img)


g.partner_class = Partner

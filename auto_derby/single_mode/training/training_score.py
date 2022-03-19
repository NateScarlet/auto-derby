# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ... import mathtools
from .globals import g
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import Context
    from .training import Training


def compute(ctx: Context, trn: Training) -> float:
    spd = mathtools.integrate(
        ctx.speed,
        trn.speed,
        ((0, 2.0), (300, 1.0), (600, 0.8), (900, 0.7), (1100, 0.5)),
    )
    if ctx.speed < ctx.turn_count() / 24 * 300:
        spd *= 1.5

    sta = mathtools.integrate(
        ctx.stamina,
        trn.stamina,
        (
            (0, 2.0),
            (300, ctx.speed / 600 + 0.3 * ctx.date[0] if ctx.speed > 600 else 1.0),
            (
                600,
                ctx.speed / 900 * 0.6 + 0.1 * ctx.date[0] if ctx.speed > 900 else 0.6,
            ),
            (900, ctx.speed / 900 * 0.3),
        ),
    )
    pow = mathtools.integrate(
        ctx.power,
        trn.power,
        (
            (0, 1.0),
            (300, 0.2 + ctx.speed / 600),
            (600, 0.1 + ctx.speed / 900),
            (900, ctx.speed / 900 / 3),
        ),
    )
    per = mathtools.integrate(
        ctx.guts,
        trn.guts,
        ((0, 2.0), (300, 1.0), (400, 0.3), (600, 0.1))
        if ctx.speed > 400 / 24 * ctx.turn_count()
        else ((0, 2.0), (300, 0.5), (400, 0.1)),
    )
    int_ = mathtools.integrate(
        ctx.wisdom,
        trn.wisdom,
        ((0, 2.0), (300, 0.8), (400, 0.1)),
    )

    vit = max(min(trn.vitality, 1 - ctx.vitality), 0) * ctx.max_vitality * 0.6
    if ctx.date[1:] in ((6, 1),):
        vit *= 1.2
    if ctx.date[1:] in ((6, 2), (7, 1), (7, 2), (8, 1)):
        vit *= 1.5
    if ctx.date[0] == 4:
        vit *= 0.3

    skill = trn.skill * 0.5

    success_rate = 1 - trn.failure_rate

    partner = 0
    for i in trn.partners:
        partner += i.score(ctx)

    target_level = g.target_levels.get(trn.type, trn.level)
    target_level_score = 0
    if ctx.is_summer_camp:
        pass
    elif trn.level < target_level:
        target_level_score += mathtools.interpolate(
            ctx.turn_count(),
            (
                (0, 5),
                (24, 3),
                (48, 2),
                (72, 0),
            ),
        )
    elif trn.level > target_level:
        target_level_score -= (trn.level - target_level) * 5

    fail_penality = 0
    if trn.type != trn.TYPE_WISDOM:
        fail_penality = mathtools.interpolate(
            ctx.turn_count(),
            (
                (0, 30),
                (72, 60),
            ),
        )

    has_hint = any(i for i in trn.partners if i.has_hint)
    hint = 3 if has_hint else 0
    return (
        (spd + sta + pow + per + int_ + skill + partner + target_level_score + hint)
        * success_rate
        + vit
        - fail_penality * trn.failure_rate
    )

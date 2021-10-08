# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from ... import mathtools

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .race import Race
    from ..context import Context


def compute(ctx: Context, race: Race) -> float:
    estimate_order = race.estimate_order(ctx)
    if estimate_order == 1:
        prop, skill = {
            race.GRADE_G1: (10, 45),
            race.GRADE_G2: (8, 35),
            race.GRADE_G3: (8, 35),
            race.GRADE_OP: (5, 35),
            race.GRADE_PRE_OP: (5, 35),
            race.GRADE_NOT_WINNING: (0, 0),
            race.GRADE_DEBUT: (0, 0),
        }[race.grade]
    elif 2 <= estimate_order <= 5:
        prop, skill = {
            race.GRADE_G1: (5, 40),
            race.GRADE_G2: (4, 30),
            race.GRADE_G3: (4, 30),
            race.GRADE_OP: (2, 20),
            race.GRADE_PRE_OP: (2, 20),
            race.GRADE_NOT_WINNING: (0, 0),
            race.GRADE_DEBUT: (0, 0),
        }[race.grade]
    else:
        prop, skill = {
            race.GRADE_G1: (4, 25),
            race.GRADE_G2: (3, 20),
            race.GRADE_G3: (3, 20),
            race.GRADE_OP: (0, 10),
            race.GRADE_PRE_OP: (0, 10),
            race.GRADE_NOT_WINNING: (0, 0),
            race.GRADE_DEBUT: (0, 0),
        }[race.grade]

    fan_count = race.fan_counts[estimate_order - 1]

    expected_fan_count = max(
        ctx.target_fan_count,
        mathtools.interpolate(
            ctx.turn_count(),
            (
                (0, 0),
                # 朝日杯フューチュリティステークス
                (18, 1000),
                # 皐月賞
                (30, 4500),
                # 日本ダービー
                (33, 6000),
                # 有馬記念
                (46, 25000),
                # valentine
                (50, 60000),
                # christmas
                (71, 120000),
            ),
        ),
    )

    fan_score = mathtools.integrate(
        ctx.fan_count,
        fan_count,
        (
            (int(expected_fan_count * 0.1), 8.0),
            (int(expected_fan_count * 0.3), 6.0),
            (int(expected_fan_count * 0.5), 4.0),
            (int(expected_fan_count), 1.0),
        ),
    ) / mathtools.interpolate(
        ctx.speed,
        (
            (0, 2400),
            (300, 1800),
            (600, 800),
            (900, 600),
        ),
    )
    if ctx.target_fan_count > ctx.fan_count:
        fan_score *= 3

    not_winning_score = 0 if ctx.is_after_winning else 1.5 * ctx.turn_count()

    continuous_race_penalty = mathtools.interpolate(
        ctx.continuous_race_count(),
        (
            (2, 0),
            (3, 5),
            (4, 25),
            (5, 50),
        ),
    )
    fail_penalty = mathtools.interpolate(
        estimate_order,
        (
            (5, 0),
            (6, 5),
            (12, 15),
        ),
    )

    status_penality = 0
    if race.distance_status(ctx) < ctx.STATUS_B:
        status_penality += 10
    if race.ground_status(ctx) < ctx.STATUS_B:
        status_penality += 10

    return (
        fan_score
        + prop
        + skill * 0.5
        + not_winning_score
        - continuous_race_penalty
        - fail_penalty
        - status_penality
    )

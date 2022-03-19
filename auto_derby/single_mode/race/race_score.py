# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

from ... import mathtools

if TYPE_CHECKING:
    from ..context import Context
    from .race import Race


def _race_reward(ctx: Context, race: Race, order: int) -> Tuple[int, int]:
    if order == 1:
        index = 0
    elif 2 <= order <= 5:
        index = 1
    else:
        index = 2

    if ctx.date[0] == 4:
        return ((30, 40), (20, 30), (10, 20))[index]
    if race.grade == race.GRADE_G1:
        return ((10, 45), (5, 40), (4, 25))[index]
    if race.grade in (race.GRADE_G2, race.GRADE_G3):
        return ((8, 35), (4, 30), (3, 20))[index]
    if race.grade in (race.GRADE_OP, race.GRADE_PRE_OP):
        return ((5, 35), (2, 20), (0, 10))[index]

    return (0, 0)


def compute(ctx: Context, race: Race) -> float:
    estimate_order = race.estimate_order(ctx)
    prop, skill = _race_reward(ctx, race, estimate_order)
    prop *= 1 + race.raward_buff
    skill *= 1 + race.raward_buff

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

    scenario_score = 0

    if ctx.scenario == ctx.SCENARIO_CLIMAX:
        grade_point = race.grade_points[estimate_order - 1]
        if ctx.grade_point < ctx.target_grade_point():
            scenario_score += grade_point * mathtools.interpolate(
                ctx.turn_count() % 24,
                (
                    (1, 0.1),
                    (24, 0.4),
                ),
            )

        shop_coin = race.shop_coins[estimate_order - 1]
        scenario_score += shop_coin * 0.02

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
        + scenario_score
        - continuous_race_penalty
        - fail_penalty
        - status_penality
    )

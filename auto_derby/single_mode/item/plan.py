# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Iterator, Sequence, Tuple

from .effect_summary import EffectSummary

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..commands import Command
    from ..context import Context
    from .item import Item

    Plan = Tuple[float, Tuple[Item, ...]]


def iterate(
    ctx: Context,
    command: Command,
    items: Sequence[Item],
    summary: EffectSummary,
) -> Iterator[Plan]:
    for index, item in enumerate(items):
        s_current = 0
        items_current: Sequence[Item] = ()
        es_after = summary.clone()
        for q_index in range(item.quantity):
            i = item.clone()
            i.quantity -= q_index
            s = i.effect_score(ctx, command, es_after)
            if s <= 0:
                break
            s_e = i.expected_effect_score(ctx, command)
            if s < s_e:
                break
            es_after.add(item)
            s_current += s
            items_current += (i,)

            yield (s_current, items_current)
            for sub_plan in iterate(
                ctx,
                command,
                (*items[:index], *items[index + 1 :]),
                es_after,
            ):
                yield ((s_current + sub_plan[0], (*items_current, *sub_plan[1])))


def compute(
    ctx: Context,
    command: Command,
) -> Plan:
    _LOGGER.debug("start compute for: %s", command)
    plan: Plan = (0, ())
    for score, items in iterate(ctx, command, tuple(ctx.items), EffectSummary()):
        if score < plan[0]:
            continue
        if score == plan[0] and sum(i.original_price for i in items) >= sum(
            i.original_price for i in plan[1]
        ):
            continue

        plan = (score, items)
        _LOGGER.debug("score: %.2f: %s", score, ",".join(i.name for i in items))
    return plan

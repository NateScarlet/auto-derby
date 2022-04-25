# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Iterator, Optional, Sequence, Tuple

from .effect_summary import EffectSummary
from .globals import g

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..commands import Command
    from ..context import Context
    from .item import Item

    Plan = Tuple[float, Tuple[Item, ...]]


def _item_order(item: Item) -> int:
    es = item.effect_summary()
    if es.training_no_failure:
        return 100
    if es.vitality:
        return 100
    if es.training_effect_buff:
        return 200
    return 300


def iterate(
    ctx: Context,
    command: Command,
    items: Sequence[Item],
    summary: EffectSummary,
) -> Iterator[Plan]:
    items = sorted(items, key=lambda x: (_item_order(x), -x.id))
    for index, item in enumerate(items):
        s_current = 0
        items_current: Sequence[Item] = ()
        es_after = summary.clone()
        for q_index in range(item.quantity):
            i = item.clone()
            i.quantity -= q_index
            # round to compare plan by price,
            # otherwise slightest difference will cause price ignored.
            s = round(i.effect_score(ctx, command, es_after), 2)
            if s <= 0:
                break
            s_e = i.expected_effect_score(ctx, command)
            if s < s_e:
                break
            i.quantity = 0  # hide quantity from log
            es_after.add(i)
            s_current += s
            items_current += (i,)

            yield (s_current, items_current)
            for sub_plan in iterate(
                ctx,
                command,
                items[index + 1 :],
                es_after,
            ):
                yield ((s_current + sub_plan[0], (*items_current, *sub_plan[1])))


def compute(
    ctx: Context,
    command: Command,
    *,
    effort: Optional[float] = None,
) -> Plan:
    effort = effort or g.default_plan_effort
    _LOGGER.debug("start compute for: %s, effort=%d", command, effort)
    deadline = time.perf_counter() + effort
    plan: Plan = (0, ())
    plan_price = 0
    for score, items in iterate(ctx, command, tuple(ctx.items), EffectSummary()):
        if time.perf_counter() > deadline:
            _LOGGER.warning(
                "effort limit reached, plan for %s may not be best", command
            )
            break
        if score < plan[0]:
            continue
        price = sum(i.original_price for i in items)
        if (score == plan[0]) and (price >= plan_price):
            continue
        plan_price = price
        plan = (score, items)
        _LOGGER.debug(
            "score:\t%.2f(%d coin)\t%s", score, price, ",".join(i.name for i in items)
        )
    return plan

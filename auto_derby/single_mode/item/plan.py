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
    def _with_log(p: Plan):
        _LOGGER.debug("score: %.2f: %s", p[0], ",".join(i.name for i in p[1]))
        return p

    yield (0, ())
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

            s_best, items_best = _with_log((s_current, items_current))
            for sub_plan in iterate(
                ctx,
                command,
                (*items[:index], *items[index + 1 :]),
                es_after,
            ):
                s_sub, items_sub = _with_log(
                    (s_current + sub_plan[0], (*items_current, *sub_plan[1]))
                )
                if s_sub > s_best:
                    s_best, items_best = s_sub, items_sub
            yield s_best, items_best

    return


def compute(
    ctx: Context,
    command: Command,
) -> Plan:
    return sorted(
        iterate(ctx, command, tuple(ctx.items), EffectSummary()),
        key=lambda x: (-x[0], sum(i.original_price for i in x[1])),
    )[0]

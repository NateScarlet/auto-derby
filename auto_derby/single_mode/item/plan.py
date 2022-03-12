# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Iterator, Sequence, Tuple

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
    picked_items: Sequence[Item] = (),
) -> Iterator[Plan]:
    def _with_log(p: Plan):
        _LOGGER.debug("plan score: %s: %s", p[0], ",".join(i.name for i in p[1]))
        return p

    for index, item in enumerate(items):
        s = item.effect_score(ctx, command, picked_items)
        if s <= 0:
            continue
        s_e = item.expected_effect_score(ctx, command)
        if s < s_e:
            continue
        sub_plans = sorted(
            iterate(
                ctx,
                command,
                (*items[:index], *items[index + 1 :]),
                (*picked_items, *(item,)),
            ),
            key=lambda x: (x[0], -sum(i.original_price for i in x[1])),
            reverse=True,
        )
        if sub_plans:
            s_sub, items_s = sub_plans[0]
            yield _with_log((s + s_sub, (item, *items_s)))
        else:
            yield _with_log((s, (item,)))

    return


def compute(
    ctx: Context,
    command: Command,
) -> Plan:
    for i in sorted(
        iterate(ctx, command, tuple(ctx.items)),
        key=lambda x: (x[0], -sum(i.original_price for i in x[1])),
        reverse=True,
    ):
        return i
    return 0, ()

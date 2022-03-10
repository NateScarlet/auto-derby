# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Sequence, Tuple

from ..context import Context
from .item import Item

if TYPE_CHECKING:
    from ..commands import Command

Plan = Tuple[float, Tuple[Item, ...]]


def iterate(
    ctx: Context,
    command: Command,
    items: Sequence[Item],
    picked_items: Sequence[Item] = (),
) -> Iterator[Plan]:
    for index, item in enumerate(items):
        s = item.effect_score(ctx, command, picked_items)
        s_e = item.expected_effect_score(ctx, command)
        if s < s_e:
            continue
        sub_plans = sorted(
            iterate(
                ctx,
                command,
                (*items[:index], *items[index + 1 :]),
                (*picked_items, *(item,)),
            )
        )
        if sub_plans:
            s_sub, items_s = sub_plans[0]
            yield s + s_sub, (item, *items_s)
        else:
            yield s, (item,)

    return


def compute(
    ctx: Context,
    command: Command,
) -> Plan:
    for i in sorted(iterate(ctx, command, tuple(ctx.items)), key=lambda x: x[0]):
        return i
    return 0, ()

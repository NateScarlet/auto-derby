from . import plan, test_sample, item_list, game_data

from ..commands import RaceCommand
from .. import race


def test_duplicated_effect():
    ctx = test_sample.simple_context()
    ctx.date = (4, 0, 0)
    ctx.speed = 1200
    ctx.stamina = 1200
    ctx.power = 1200
    ctx.items.put(51, 2)
    race.reload_on_demand()
    s, items = plan.compute(
        ctx,
        RaceCommand(next(i for i in race.g.races if i.name == "トゥインクルスタークライマックス 第3戦")),
    )
    assert s > 0
    assert len(items) == 1

from auto_derby.constants import TrainingType
from auto_derby.single_mode.commands.training import TrainingCommand
from auto_derby.single_mode.training.training import Training
from . import plan, test_sample, item_list, game_data
from .globals import g

from ..commands import RaceCommand
from .. import race
from ... import _test

g.explain_score = True


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


def test_duplicated_training_buff():
    ctx = test_sample.simple_context()
    ctx.date = (3, 12, 2)
    ctx.speed = 1008
    ctx.stamina = 687
    ctx.power = 777
    ctx.guts = 460
    ctx.wisdom = 406
    ctx.items.put(16, 4)
    ctx.items.put(17, 2)
    ctx.items.put(45, 1)
    ctx.items.put(44, 2)
    ctx.items.put(43, 2)
    ctx.items.put(47, 2)
    ctx.items.put(50, 1)
    t = Training.new()
    t.type = TrainingType.STAMINA
    t.stamina = 15
    t.guts = 5
    t.skill = 3
    t.vitality = -0.21
    t.failure_rate = 0.47
    s, items = plan.compute(ctx, TrainingCommand(t), effort=float("inf"))
    assert s > 0
    _test.snapshot_match(",".join(i.name for i in items))

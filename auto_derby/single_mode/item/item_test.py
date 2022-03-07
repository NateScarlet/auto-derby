from . import game_data
from .. import race, training
from ..context import Context
from ..commands import RaceCommand, TrainingCommand


def test_effect_score():
    ctx = Context.new()
    ctx.head = ctx.STATUS_A
    ctx.lead = ctx.STATUS_A
    ctx.middle = ctx.STATUS_A
    ctx.last = ctx.STATUS_A
    ctx.turf = ctx.STATUS_A
    ctx.dart = ctx.STATUS_A
    ctx.sprint = ctx.STATUS_A
    ctx.mile = ctx.STATUS_A
    ctx.intermediate = ctx.STATUS_A
    ctx.long = ctx.STATUS_A
    power_memo = game_data.get(3)
    assert power_memo
    power_memo.price = power_memo.original_price
    assert power_memo.effect_score(ctx, RaceCommand(next(race.game_data.find_by_date((1,0,0))))) == 0
    assert power_memo.effect_score(ctx, TrainingCommand(training.Training.new())) > 0
    assert power_memo.exchange_score(ctx) > 0

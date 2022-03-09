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
    ctx.speed = 600
    ctx.stamina = 600
    ctx.power = 600
    ctx.guts = 600
    ctx.wisdom = 600
    power_memo = game_data.get(3)
    power_memo.price = power_memo.original_price
    assert (
        power_memo.effect_score(
            ctx, RaceCommand(next(race.game_data.find_by_date((1, 0, 0))))
        )
        == 0
    )
    assert power_memo.effect_score(ctx, TrainingCommand(training.Training.new())) > 0
    assert power_memo.exchange_score(ctx) > 0

    hammer_1 = game_data.get(51)
    hammer_1.price = hammer_1.original_price
    # assert hammer_1.effect_score(ctx, RaceCommand(next(race.game_data.find_by_date((4,0,0))))) >0
    assert hammer_1.effect_score(ctx, TrainingCommand(training.Training.new())) == 0
    # assert hammer_1.exchange_score(ctx) > 0

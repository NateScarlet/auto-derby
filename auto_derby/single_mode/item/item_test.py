from ... import _test
from ...constants import Mood, TrainingType
from .. import race, training
from ..commands import RaceCommand, TrainingCommand
from ..context import Context
from ..training import Training
from . import game_data


def _sample_context():
    ctx1 = Context.new()
    ctx1.date = (1, 7, 1)
    ctx1.head = ctx1.STATUS_A
    ctx1.lead = ctx1.STATUS_A
    ctx1.middle = ctx1.STATUS_A
    ctx1.last = ctx1.STATUS_A
    ctx1.turf = ctx1.STATUS_A
    ctx1.dart = ctx1.STATUS_A
    ctx1.sprint = ctx1.STATUS_A
    ctx1.mile = ctx1.STATUS_A
    ctx1.intermediate = ctx1.STATUS_A
    ctx1.long = ctx1.STATUS_A
    ctx1.speed = 200
    ctx1.stamina = 200
    ctx1.power = 150
    ctx1.guts = 150
    ctx1.wisdom = 150
    ctx1.vitality = 0.7
    ctx1.trainings = tuple(i for _, i in _sample_trainings())
    yield "year1", ctx1

    ctx = ctx1.from_dict(ctx1.to_dict())
    ctx.mood = Mood.VERY_GOOD
    ctx.trainings = tuple(i for _, i in _sample_trainings())
    yield "year1-mood-very-good", ctx

    ctx2 = Context.new()
    ctx2.date = (2, 1, 1)
    ctx2.head = ctx2.STATUS_A
    ctx2.lead = ctx2.STATUS_A
    ctx2.middle = ctx2.STATUS_A
    ctx2.last = ctx2.STATUS_A
    ctx2.turf = ctx2.STATUS_A
    ctx2.dart = ctx2.STATUS_A
    ctx2.sprint = ctx2.STATUS_A
    ctx2.mile = ctx2.STATUS_A
    ctx2.intermediate = ctx2.STATUS_A
    ctx2.long = ctx2.STATUS_A
    ctx2.speed = 400
    ctx2.stamina = 300
    ctx2.power = 300
    ctx2.guts = 200
    ctx2.wisdom = 200
    ctx2.vitality = 0.7
    ctx2.trainings = tuple(i for _, i in _sample_trainings())
    yield "year2", ctx2

    ctx = ctx2.from_dict(ctx2.to_dict())
    ctx.vitality = 1.0
    ctx.trainings = tuple(i for _, i in _sample_trainings())
    yield "year2-vitality-100", ctx

    ctx3 = Context.new()
    ctx3.date = (3, 1, 1)
    ctx3.head = ctx3.STATUS_A
    ctx3.lead = ctx3.STATUS_A
    ctx3.middle = ctx3.STATUS_A
    ctx3.last = ctx3.STATUS_A
    ctx3.turf = ctx3.STATUS_A
    ctx3.dart = ctx3.STATUS_A
    ctx3.sprint = ctx3.STATUS_A
    ctx3.mile = ctx3.STATUS_A
    ctx3.intermediate = ctx3.STATUS_A
    ctx3.long = ctx3.STATUS_A
    ctx3.speed = 900
    ctx3.stamina = 600
    ctx3.power = 600
    ctx3.guts = 400
    ctx3.wisdom = 400
    ctx3.vitality = 0.7
    ctx3.trainings = tuple(i for _, i in _sample_trainings())
    yield "year3", ctx3


def _sample_trainings():
    t = Training.new()
    t.type = TrainingType.SPEED
    t.speed = 10
    t.vitality = -0.3
    yield "speed-10", t

    t = Training.new()
    t.type = TrainingType.STAMINA
    t.stamina = 10
    t.vitality = -0.3
    yield "stamina-10", t

    t = Training.new()
    t.type = TrainingType.POWER
    t.power = 10
    t.vitality = -0.3
    yield "power-10", t

    t = Training.new()
    t.type = TrainingType.GUTS
    t.guts = 10
    t.vitality = -0.4
    yield "guts-10", t

    t = Training.new()
    t.type = TrainingType.WISDOM
    t.wisdom = 10
    t.vitality = 0.1
    yield "wisdom-10", t


def _sample_races():
    race.game_data.reload_on_demand()
    names = {
        "ジュニア級未勝利戦",
        "朝日杯フューチュリティステークス",
        "東京優駿（日本ダービー）",
        "菊花賞",
        "スプリンターズステークス",
        "有馬記念",
        "ジャパンダートダービー",
    }
    for i in race.game_data.g.races:
        if i.name in names:
            yield i
            names.remove(i.name)


def _iterate_item():
    for i in game_data.iterate():
        i.price = i.original_price
        yield i


def test_property_item():
    for name, ctx in _sample_context():
        _test.snapshot_match(
            {
                i.name: {
                    "exchange": i.exchange_score(ctx),
                    "expectedExchange": i.expected_exchange_score(ctx),
                    "shouldUseDirectly": i.should_use_directly(ctx),
                }
                for i in _iterate_item()
                if any(e for e in i.effects if e.type == e.TYPE_PROPERTY)
            },
            name=name,
        )


def test_training_buff_item():
    for name, ctx in _sample_context():
        _test.snapshot_match(
            {
                i.name: {
                    "exchange": i.exchange_score(ctx),
                    "expectedExchange": i.expected_exchange_score(ctx),
                    "shouldUseDirectly": i.should_use_directly(ctx),
                    "training": {
                        t_name: {
                            "effect": i.effect_score(ctx, TrainingCommand(t)),
                            "expectedEffect": i.expected_effect_score(
                                ctx, TrainingCommand(t)
                            ),
                        }
                        for t_name, t in _sample_trainings()
                    },
                    "maxRaceEffect": max(
                        (i.effect_score(ctx, RaceCommand(r)) for r in _sample_races())
                    ),
                }
                for i in _iterate_item()
                if any(e for e in i.effects if e.type == e.TYPE_TRAINING_BUFF)
            },
            name=name,
        )


def test_race_reward_item():
    hammer_1 = game_data.get(51)
    hammer_1.price = hammer_1.original_price
    # assert hammer_1.effect_score(ctx, RaceCommand(next(race.game_data.find_by_date((4,0,0))))) >0
    for name, ctx in _sample_context():
        assert hammer_1.effect_score(ctx, TrainingCommand(training.Training.new())) == 0
    # assert hammer_1.exchange_score(ctx) > 0

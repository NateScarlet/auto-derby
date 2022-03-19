from ...constants import Mood, TrainingType
from .. import race

from ..context import Context
from ..training import Training


def simple_context():
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
    ctx1.trainings = tuple(i for _, i in trainings())
    return ctx1


def contexts():
    yield "year1", simple_context()

    ctx = simple_context()
    ctx.vitality = 0
    yield "year1-vitality-0", ctx

    ctx = simple_context()
    ctx.mood = Mood.VERY_GOOD
    ctx.trainings = tuple(i for _, i in trainings())
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
    ctx2.trainings = tuple(i for _, i in trainings())
    yield "year2", ctx2

    ctx = ctx2.clone()
    ctx.vitality = 1.0
    ctx.trainings = tuple(i for _, i in trainings())
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
    ctx3.trainings = tuple(i for _, i in trainings())
    yield "year3", ctx3


def trainings():
    t = Training.new()
    t.type = TrainingType.SPEED
    t.speed = 10
    t.vitality = -0.3
    t.failure_rate = 0.05
    yield "speed-10", t

    t = Training.new()
    t.type = TrainingType.STAMINA
    t.stamina = 10
    t.vitality = -0.3
    t.failure_rate = 0.05
    yield "stamina-10", t

    t = Training.new()
    t.type = TrainingType.POWER
    t.power = 10
    t.vitality = -0.3
    t.failure_rate = 0.05
    yield "power-10", t

    t = Training.new()
    t.type = TrainingType.GUTS
    t.guts = 10
    t.vitality = -0.4
    t.failure_rate = 0.05
    yield "guts-10", t

    t = Training.new()
    t.type = TrainingType.WISDOM
    t.wisdom = 10
    t.vitality = 0.1
    t.failure_rate = 0.02
    yield "wisdom-10", t

    t = Training.new()
    t.type = TrainingType.SPEED
    t.speed = 10
    t.vitality = -0.3
    t.failure_rate = 0.4
    yield "speed-10-fail-40", t


def races():
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

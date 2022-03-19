from auto_derby.single_mode.item.effect_summary import EffectSummary
from ... import _test
from ...constants import Mood, TrainingType
from .. import race, training
from ..commands import RaceCommand, TrainingCommand
from ..context import Context
from ..training import Training
from . import game_data
from . import test_sample


def _iterate_item():
    for i in game_data.iterate():
        i.price = i.original_price
        yield i


def test_property_item():
    for name, ctx in test_sample.contexts():
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
    for name, ctx in test_sample.contexts():
        _test.snapshot_match(
            {
                i.name: {
                    "exchange": i.exchange_score(ctx),
                    "expectedExchange": i.expected_exchange_score(ctx),
                    "shouldUseDirectly": i.should_use_directly(ctx),
                    "training": {
                        t_name: {
                            "effect": i.effect_score(
                                ctx, TrainingCommand(t), EffectSummary()
                            ),
                            "expectedEffect": i.expected_effect_score(
                                ctx, TrainingCommand(t)
                            ),
                        }
                        for t_name, t in test_sample.trainings()
                    },
                    "maxRaceEffect": max(
                        (
                            i.effect_score(ctx, RaceCommand(r), EffectSummary())
                            for r in test_sample.races()
                        )
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
    for name, ctx in test_sample.contexts():
        assert (
            hammer_1.effect_score(
                ctx, TrainingCommand(training.Training.new()), EffectSummary()
            )
            == 0
        )
    # assert hammer_1.exchange_score(ctx) > 0

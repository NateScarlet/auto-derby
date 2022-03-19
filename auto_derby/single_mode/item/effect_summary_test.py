from auto_derby.single_mode.race.race import Race
from . import game_data
from . import test_sample

from ... import _test


def _iter_effect_summarys():
    for i in game_data.iterate():
        yield i.name, i.effect_summary()


def test_apply_to_context():
    for name, ctx in test_sample.contexts():
        _test.snapshot_match(
            {name: es.apply_to_context(ctx) for name, es in _iter_effect_summarys()},
            name=name,
        )


def test_apply_to_training():
    for name, ctx in test_sample.contexts():
        _test.snapshot_match(
            {
                name: {
                    t_name: es.apply_to_training(ctx, t)
                    for t_name, t in test_sample.trainings()
                }
                for name, es in _iter_effect_summarys()
                if es.training_effect_buff or es.training_vitality_debuff
            },
            name=name,
        )


def test_reduce_on_training():
    _test.snapshot_match(
        {
            name: {
                t_name: es.reduce_on_training(t)[0]
                for t_name, t in test_sample.trainings()
            }
            for name, es in _iter_effect_summarys()
            if es.training_effect_buff or es.training_vitality_debuff
        },
    )


def _race_buff_data(r: Race):
    return {"rewardBuff": r.raward_buff, "fanCounts": r.fan_counts}


def test_apply_to_race():
    ctx = test_sample.simple_context()
    _test.snapshot_match(
        {
            name: {
                r.name: _race_buff_data(es.apply_to_race(ctx, r))
                for r in test_sample.races()
            }
            for name, es in _iter_effect_summarys()
            if es.race_fan_buff or es.race_reward_buff
        },
    )

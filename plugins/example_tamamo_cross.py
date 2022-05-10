# -*- coding=UTF-8 -*-

from typing import Tuple

import auto_derby
from auto_derby import app, mathtools
from auto_derby.single_mode.context import Context
from auto_derby.single_mode.race import race_result
from auto_derby.single_mode.race.race import Race


class _g:
    cached_is_year2_target_pending: Tuple[Tuple[int, int, int], bool] = (
        (0, 0, 0),
        False,
    )


def _raw_is_year2_target_pending(ctx: Context) -> bool:
    if ctx.date < (2, 1, 1) or ctx.date > (3, 1, 1):
        return False

    winning_count = 0
    for i in race_result.iterate_current(ctx):
        if i.race.grade <= Race.GRADE_G3 and i.order <= 3:
            winning_count += 1
        if winning_count >= 4:
            return False
    app.log.text("year2 target pending: %d/4" % winning_count)
    return True


def _is_year2_target_pending(ctx: Context) -> bool:
    if ctx.date != _g.cached_is_year2_target_pending[0]:
        _g.cached_is_year2_target_pending = (
            ctx.date,
            _raw_is_year2_target_pending(ctx),
        )
    return _g.cached_is_year2_target_pending[1]


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        class Race(auto_derby.config.single_mode_race_class):
            def score(self, ctx: Context) -> float:
                ret = super().score(ctx)
                if (
                    self.grade <= Race.GRADE_G3
                    and _is_year2_target_pending(ctx)
                    and self.estimate_order(ctx) <= 5
                ):
                    ret += mathtools.interpolate(
                        ctx.turn_count(),
                        (
                            (24, 10.0),
                            (48, 100.0),
                        ),
                    )

                return ret

        auto_derby.config.single_mode_race_class = Race


auto_derby.plugin.register(__name__, Plugin())

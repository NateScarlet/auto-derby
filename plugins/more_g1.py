import auto_derby
from auto_derby import single_mode


class Plugin(auto_derby.Plugin):
    """Use this after other plugin, increase g1 score if estimate order <= 3."""

    def install(self) -> None:
        class Race(auto_derby.config.single_mode_race_class):
            def score(self, ctx: single_mode.Context) -> float:
                ret = super().score(ctx)
                if self.grade == Race.GRADE_G1 and self.estimate_order(ctx) <= 3:
                    ret += 5
                else:
                    ret -= 5
                return ret

        auto_derby.config.single_mode_race_class = Race


auto_derby.plugin.register(__name__, Plugin())

# Deprecated: remove at next major version
auto_derby.plugin.register("prefer_g1", Plugin())

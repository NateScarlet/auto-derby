import auto_derby
from auto_derby import single_mode


class Plugin(auto_derby.Plugin):
    """Use this after other plugin, reduce op/pre-op race score."""

    def install(self) -> None:
        class Race(auto_derby.config.single_mode_race_class):
            def score(self, ctx: single_mode.Context) -> float:
                ret = super().score(ctx)
                if self.grade in (Race.GRADE_OP, Race.GRADE_PRE_OP):
                    ret -= 10
                return ret

        auto_derby.config.single_mode_race_class = Race


auto_derby.plugin.register(__name__, Plugin())

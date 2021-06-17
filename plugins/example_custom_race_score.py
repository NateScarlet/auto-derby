import auto_derby
from auto_derby import single_mode


class Race(single_mode.Race):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
        if self.name == "有馬記念":
            ret += 10
        return ret


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.SINGLE_MODE_RACE_CLASS = Race


auto_derby.plugin.register(__name__, Plugin())

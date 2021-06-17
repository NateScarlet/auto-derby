import auto_derby
from auto_derby import single_mode


class Training(single_mode.Training):
    def score(self, ctx: single_mode.Context) -> float:
        ret = super().score(ctx)
        ret += self.stamina * 0.3
        return ret


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_training_class = Training


auto_derby.plugin.register(__name__, Plugin())

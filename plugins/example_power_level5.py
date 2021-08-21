import auto_derby
from auto_derby import single_mode


class Plugin(auto_derby.Plugin):
    """Earn second name `努力の天才`"""

    def install(self) -> None:
        class Training(auto_derby.config.single_mode_training_class):
            def score(self, ctx: single_mode.Context) -> float:
                ret = super().score(ctx)
                if self.type == self.TYPE_POWER and self.level < 5:
                    ret += 5
                return ret

        auto_derby.config.single_mode_training_class = Training


auto_derby.plugin.register(__name__, Plugin())

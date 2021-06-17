import auto_derby
from auto_derby import single_mode


class Context(single_mode.Context):
    def next_turn(self) -> None:
        super().next_turn()
        auto_derby.config.pause_if_race_order_gt = {
            1: 5,
            2: 3,
            3: 2,
            4: 1,
        }[self.date[0]]


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        auto_derby.config.single_mode_context_class = Context


auto_derby.plugin.register(__name__, Plugin())

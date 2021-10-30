import auto_derby
from auto_derby import terminal


class Plugin(auto_derby.Plugin):
    """Pause on last turn, not work when start from year 4."""

    def install(self) -> None:
        class Context(auto_derby.config.single_mode_context_class):
            def next_turn(self):
                super().next_turn()
                if self.turn_count() == self.total_turn_count():
                    terminal.pause(f"pause on last turn")

        auto_derby.config.single_mode_context_class = Context


auto_derby.plugin.register(__name__, Plugin())

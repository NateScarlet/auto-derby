from auto_derby.single_mode.commands.race import RaceResult
from auto_derby.single_mode.context import Context
import auto_derby
from auto_derby import terminal


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        _next = auto_derby.config.on_single_mode_race_result

        def _handle(ctx: Context, result: RaceResult):
            if result.is_failed:
                terminal.pause(f"pause before continue race: {result}")
            _next(ctx, result)

        auto_derby.config.on_single_mode_race_result = _handle


auto_derby.plugin.register(__name__, Plugin())

import auto_derby
from auto_derby.single_mode import Context, RaceResult


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        def _should_retry_race(ctx: Context, result: RaceResult) -> bool:
            return False

        auto_derby.config.single_mode_should_retry_race = _should_retry_race


auto_derby.plugin.register(__name__, Plugin())

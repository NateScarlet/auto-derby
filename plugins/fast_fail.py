from enum import auto
import auto_derby
from auto_derby import app
from auto_derby.single_mode import Context, Race, Training, item, go_out
from auto_derby.single_mode.commands import Command

from auto_derby.single_mode.item import EffectSummary
from auto_derby.scenes.single_mode import CommandScene


class Plugin(auto_derby.Plugin):
    """End nurturing fast by failing."""

    def install(self) -> None:
        class _Race(Race):
            def score(self, ctx: Context) -> float:
                return 0

        class _Training(Training):
            def score(self, ctx: Context) -> float:
                return 0

        class _Item(item.Item):
            def effect_score(
                self, ctx: Context, command: Command, summary: EffectSummary
            ) -> float:
                return 0

            def exchange_score(self, ctx: Context) -> float:
                return 0

            def should_use_directly(self, ctx: Context) -> bool:
                return False

        class _GoOutOption(go_out.Option):
            def score(self, ctx: Context) -> float:
                return 0

        class _Context(Context):
            @property
            def shop_coin(self):
                return 0

            @shop_coin.setter
            def shop_coin(self, v):
                pass

            def next_turn(self) -> None:
                super().next_turn()
                app.log.text(
                    "plugin `fast_fail` installed, nurturing is expected to fail",
                    level=app.WARN,
                )

        CommandScene.max_recognition_retry = 0
        auto_derby.config.single_mode_ignore_training_commands = lambda *_, **__: True
        auto_derby.config.single_mode_should_retry_race = lambda *_, **__: False
        auto_derby.config.single_mode_race_class = _Race
        auto_derby.config.ocr_prompt_disabled = True
        auto_derby.config.single_mode_event_prompt_disabled = True
        auto_derby.config.single_mode_item_prompt_disabled = True
        auto_derby.config.single_mode_training_class = _Training
        auto_derby.config.single_mode_item_class = _Item
        auto_derby.config.single_mode_go_out_option_class = _GoOutOption
        auto_derby.config.single_mode_rest_score = lambda ctx: 100
        auto_derby.config.single_mode_summer_rest_score = lambda ctx: 100
        auto_derby.config.single_mode_context_class = _Context


auto_derby.plugin.register(__name__, Plugin())

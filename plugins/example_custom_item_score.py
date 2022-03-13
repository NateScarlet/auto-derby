import auto_derby
from auto_derby.constants import TrainingType
from auto_derby.single_mode.commands import Command, TrainingCommand, RaceCommand
from auto_derby.single_mode import Context
from auto_derby.single_mode.item import EffectSummary


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        class Item(auto_derby.config.single_mode_item_class):
            # high exchange score means high exchange priority
            def exchange_score(self, ctx: Context) -> float:
                ret = super().exchange_score(ctx)
                # increase for "プリティーミラー"
                if self.name == "プリティーミラー":
                    ret += 10
                return ret

            # item will not be exchanged from shop if 
            # exchange score less than expected exchange score
            def expected_exchange_score(self, ctx: Context) -> float:
                ret = super().expected_exchange_score(ctx)
                # increase for wisdom training buff
                es = self.effect_summary()
                if any(i.type == TrainingType.WISDOM for i in es.training_effect_buff):
                    ret += 10
                return ret

            # effect score will be added to command score.
            # all items that effect score greater than expected effect score
            # will be used before command execute.
            # also affect default exchange score.
            def effect_score(
                self, ctx: Context, command: Command, summary: EffectSummary
            ) -> float:
                ret = super().effect_score(ctx, command, summary)
                # increase for "スピードアンクルウェイト"
                if (
                    isinstance(command, TrainingCommand)
                    and command.training.type == TrainingType.SPEED
                    and self.name == "スピードアンクルウェイト"
                ):
                    ret += 10
                return ret

            def expected_effect_score(self, ctx: Context, command: Command) -> float:
                ret = super().expected_effect_score(ctx, command)
                # reduce when training speed > 30
                if isinstance(command, TrainingCommand) and command.training.speed > 30:
                    ret -= 10
                # increase  when race grade lower than G1
                if (
                    isinstance(command, RaceCommand)
                    and command.race.grade > command.race.GRADE_G1
                ):
                    ret += 10
                return ret

            def should_use_directly(self, ctx: Context) -> bool:
                # use max vitality item directly after exchange
                es = self.effect_summary()
                if es.max_vitality > 0:
                    return True
                return super().should_use_directly(ctx)

        auto_derby.config.single_mode_item_class = Item


auto_derby.plugin.register(__name__, Plugin())

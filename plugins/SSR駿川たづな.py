from typing import Callable, List
import auto_derby
from auto_derby import mathtools
from auto_derby.single_mode import Context
from auto_derby.__version__ import VERSION
from auto_derby import version


_NAME = "駿川たづな"

_VIT = [0, 0, 0, 0, 0]
_SPD = [0, 0, 0, 0, 0]
_MOOD = [0, 0, 0, 0, 0]
_HEAL = [0, 0, 0, 0, 0]
_STA = [0, 0, 0, 0, 0]
_WIS = [0, 0, 0, 0, 0]
_SKILL = [0, 0, 0, 0, 0]

## 牛乳ときどきリンゴ（お出かけ1）
# 体力+25~40
_VIT[0] = 30
# スピード(速度)+5~6
_SPD[0] = 5
# やる気(干劲)アップ(提升)
_MOOD[0] = 1
# 駿川たづなの絆ゲージ+5


## 驚異の逃げ脚？（お出かけ2）
# 体力+25~40
_VIT[1] = 32
# 駿川たづなの絆ゲージ+5
# バッドコンディションが治る
_HEAL[1] = 1

## キネマの思ひ出（お出かけ3）
### 『200億の女～キケンな専業主婦～』
# 体力+25~40
_VIT[2] = 32
# スタミナ(耐力)+5~6
_STA[2] = 5
# やる気(干劲)アップ(提升)
_MOOD[2] = 1
# 駿川たづなの絆ゲージ+5
### 『白球ひと筋、空へ――熱血野球部物語！』
# スタミナ(耐力)+10~13
# 根性(毅力)+10~13
# やる気(干劲)アップ(提升)
# 駿川たづなの絆ゲージ+5

### ため息と絆創膏（お出かけ4）
# 体力+35~56
_VIT[3] = 45
# 賢さ(智力)+5~6
_WIS[3] = 5
# やる気(干劲)アップ(提升)
_MOOD[3] = 1
# 駿川たづなの絆ゲージ+5
# バッドコンディションが治る
_HEAL[3] = 1

###ひと休みサプライズ（お出かけ5）
# 体力+35~56
_VIT[4] = 45
# スキルPt(技能点数)+30~40
_SKILL[4] = 35
# やる気(干劲)2段階アップ(提升)
_MOOD[4] = 2
# 駿川たづなの絆ゲージ+5
# 以下からランダムで(有概率)獲得
# 『集中力』のヒントLv+1
# 『コンセントレーション』のヒントLv+1


class Plugin(auto_derby.Plugin):
    """
    Use this when friend cards include SSR駿川たづな.
    Multiple friend type support card is not supported.
    """

    def install(self) -> None:
        auto_derby.config.single_mode_go_out_names.add(_NAME)

        class Option(auto_derby.config.single_mode_go_out_option_class):
            def heal_rate(self, ctx: Context) -> float:
                if self.name != _NAME:
                    return super().heal_rate(ctx)

                return _HEAL[self.current_event_count]

            def mood_rate(self, ctx: Context) -> float:
                if self.name != _NAME:
                    return super().mood_rate(ctx)

                return _MOOD[self.current_event_count]

            def vitality(self, ctx: Context) -> float:
                if self.name != _NAME:
                    return super().vitality(ctx)

                return _VIT[self.current_event_count] / ctx.max_vitality

            def score(self, ctx: Context) -> float:
                ret = super().score(ctx)
                if self.name != _NAME:
                    return ret

                t = Training()
                c = self.current_event_count
                t.wisdom = _WIS[c]
                t.stamina = _STA[c]
                t.speed = _SPD[c]
                t.skill = _SKILL[c]
                ret += t.score(ctx)

                return ret

        auto_derby.config.single_mode_go_out_option_class = Option

        class Training(auto_derby.config.single_mode_training_class):
            def score(self, ctx: Context) -> float:
                try:
                    partner = next(i for i in self.partners if i.type == i.TYPE_FRIEND)
                except StopIteration:
                    return super().score(ctx)

                cleanup: List[Callable[[], None]] = []
                # assume lv 50 effect
                # https://github.com/NateScarlet/auto-derby/issues/160
                if getattr(self, "_use_estimate_vitality", False) and self.vitality < 0:
                    _orig_vit = self.vitality

                    def _c1():
                        self.vitality = _orig_vit

                    self.vitality *= 0.7

                    cleanup.append(_c1)
                # https://github.com/NateScarlet/auto-derby/issues/152
                if getattr(self, "_use_estimate_failure_rate", False):
                    _orig_failure = self.failure_rate

                    def _c2():
                        self.failure_rate = _orig_failure

                    self.failure_rate *= 0.6

                    cleanup.append(_c2)

                ret = super().score(ctx)
                for i in cleanup:
                    i()

                if partner.level < 4:
                    ret += mathtools.interpolate(
                        ctx.turn_count(),
                        (
                            (0, 10),
                            (24, 12),
                            (48, 20),
                            (72, 20),
                        ),
                    )
                elif not ctx.go_out_options:
                    # go out unlock event not happened
                    ret += 10
                return ret

        auto_derby.config.single_mode_training_class = Training


auto_derby.plugin.register(__name__, Plugin())

from typing import Callable, List
import auto_derby
from auto_derby.single_mode import Context


_NAME = "樫本理子"

_VIT = [0, 0, 0, 0, 0]
_MOOD = [0, 0, 0, 0, 0]
_HEAL = [0, 0, 0, 0, 0]
_SPD = [0, 0, 0, 0, 0]
_STA = [0, 0, 0, 0, 0]
_POW = [0, 0, 0, 0, 0]
_GUT = [0, 0, 0, 0, 0]
_WIS = [0, 0, 0, 0, 0]
_SKILL = [0, 0, 0, 0, 0]


# https://gamewith.jp/uma-musume/article/show/292758

## 歌には想いを乗せて（お出かけ1）
# 体力+30～32
_VIT[0] = 30
# やる気(干劲)アップ(提升)
_MOOD[0] = 1
# スタミナ(耐力)+12～13
_STA[0] = 12
# 樫本理子の絆ゲージ+5


## ひとときの休息を（お出かけ2）
# 体力+24～26
_VIT[1] = 25
# やる気(干劲)アップ(提升)
_MOOD[1] = 1
# スタミナ(耐力)+12～13
_STA[1] = 12
# 根性(毅力)+12～13
_GUT[1] = 12
# 樫本理子の絆ゲージ+5

## 喜ぶ顔を思い浮かべて（お出かけ3）
### ここは『大容量ハチミルク』で！
# 体力+24～26
_VIT[2] = 25
# やる気アップ
_MOOD[2] = 1
# スタミナ+12～13
_STA[2] = 12
# 根性+6
_GUT[2] = 6
# 樫本理子の絆ゲージ+5
### やはり『ウマスタ映えソーダ』で！
# スキルpt+37～40
# やる気アップ
# 樫本理子の絆ゲージ+5

## 向けられる想いと戸惑い（お出かけ4）
# 体力+24～26
_VIT[3] = 25
# やる気アップ
_MOOD[3] = 1
# スピード+12～13
_SPD[3] = 12
# スタミナ+6
_STA[3] = 6
# パワー+6
_POW[3] = 6
# 樫本理子の絆ゲージ+5

## 胸の内を少しだけ（お出かけ5）
### 成功時：
# 体力+30～32
_VIT[4] = 31
# やる気アップ
_MOOD[4] = 1
# スタミナ+12～13
_STA[4] = 12
# 根性+12～13
_GUT[4] = 12
# 『一陣の風』のヒントLv+3
# 樫本理子の絆ゲージ+5
### 失敗時：
# 体力+30～32
# やる気アップ
# スタミナ+6
# 根性+6
# 『一陣の風』のヒントLv+1
# 樫本理子の絆ゲージ+5


class Plugin(auto_derby.Plugin):
    """
    Use this when friend cards include SSR樫本理子.
    Multiple friend type support card is not supported yet.
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
                t.speed = _SPD[c]
                t.stamina = _STA[c]
                t.power = _POW[c]
                t.guts = _GUT[c]
                t.wisdom = _WIS[c]
                t.skill = _SKILL[c]
                ret += t.score(ctx)

                return ret

        auto_derby.config.single_mode_go_out_option_class = Option

        class Training(auto_derby.config.single_mode_training_class):
            def score(self, ctx: Context) -> float:
                try:
                    next(i for i in self.partners if i.type == i.TYPE_FRIEND)
                except StopIteration:
                    return super().score(ctx)

                cleanup: List[Callable[[], None]] = []
                # assume lv 50 effect
                # https://github.com/NateScarlet/auto-derby/issues/160
                if getattr(self, "_use_estimate_vitality", False) and self.vitality < 0:
                    _orig_vit = self.vitality

                    def _c1():
                        self.vitality = _orig_vit

                    self.vitality *= 0.8

                    cleanup.append(_c1)

                ret = super().score(ctx)
                for i in cleanup:
                    i()

                return ret

        auto_derby.config.single_mode_training_class = Training


auto_derby.plugin.register(__name__, Plugin())

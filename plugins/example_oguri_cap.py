# -*- coding=UTF-8 -*-
# Code generated by auto-derby-plugin-generator 16460f6
# URL: https://natescarlet.github.io/auto-derby-plugin-generator/#/plugins/race
# Date: 2021-11-30T16:54:12.152Z

import auto_derby
from auto_derby import single_mode


from typing import Text, Dict, Tuple

_ACTION_NONE = 0
_ACTION_BAN = 1
_ACTION_LESS = 2
_ACTION_MORE = 3
_ACTION_PICK = 4

_DEFAULT_ACTION = _ACTION_NONE

_RULES: Dict[Tuple[int, Text], int] = {
    (53, "大阪杯"): _ACTION_PICK,
    (56, "ヴィクトリアマイル"): _ACTION_MORE,
    (58, "安田記念"): _ACTION_MORE,
    (59, "宝塚記念"): _ACTION_MORE,
}


class Plugin(auto_derby.Plugin):
    def install(self) -> None:
        class Race(auto_derby.config.single_mode_race_class):
            def score(self, ctx: single_mode.Context) -> float:
                ret = super().score(ctx)
                action = _RULES.get(
                    (ctx.turn_count(), self.name),
                    _DEFAULT_ACTION,
                )
                if action == _ACTION_BAN:
                    ret = 0
                elif action == _ACTION_LESS:
                    ret -= 5
                elif action == _ACTION_MORE:
                    ret += 5
                elif action == _ACTION_PICK:
                    ret += 100
                return ret

        auto_derby.config.single_mode_race_class = Race


auto_derby.plugin.register(__name__, Plugin())

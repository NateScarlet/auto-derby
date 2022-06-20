# -*- coding=UTF-8 -*-

import datetime
from abc import abstractmethod
from typing import List, Text

import auto_derby
from auto_derby import app, single_mode
from auto_derby.single_mode.context import Context
from auto_derby.single_mode.race import race_result
from auto_derby.single_mode.race.race import Race

JST = datetime.timezone(datetime.timedelta(hours=9), name="JST")


class Campaign:
    def __init__(
        self,
        start: datetime.datetime,
        end: datetime.datetime,
        race_name: Text,
    ) -> None:
        self.start = start
        self.end = end
        self.race_name = race_name
        super().__init__()

    @abstractmethod
    def match(self, ctx: Context, race: Race) -> bool:
        if race.name != self.race_name:
            return False
        now = datetime.datetime.now(JST)
        if not (self.start <= now <= self.end):
            return False
        return True


class OncePerDayCampaign(Campaign):
    def __init__(
        self,
        start: datetime.datetime,
        end: datetime.datetime,
        race_name: Text,
        *,
        order_lte: int = 999,
    ) -> None:
        super().__init__(
            start,
            end,
            race_name,
        )
        self.order_lte = order_lte

    def match(self, ctx: Context, race: Race) -> bool:
        if not super().match(ctx, race):
            return False
        for r in race_result.iterate():
            if (
                r.race.name == race.name
                and r.order <= self.order_lte
                and r.time.astimezone(JST).date() == datetime.datetime.now(JST).date()
            ):
                return False

        return True


class OneTimeCampaign(Campaign):
    def __init__(
        self,
        start: datetime.datetime,
        end: datetime.datetime,
        race_name: Text,
        *,
        order_lte: int = 999,
    ) -> None:
        super().__init__(
            start,
            end,
            race_name,
        )
        self.order_lte = order_lte

    def match(self, ctx: Context, race: Race) -> bool:
        if not super().match(ctx, race):
            return False
        for r in race_result.iterate():
            if (
                r.race.name == race.name
                and r.order <= self.order_lte
                and self.start < r.time.astimezone(JST) <= self.end
            ):
                return False

        return True


_CAMPAIGNS: List[Campaign] = []


def _add_campaign(
    c: Campaign,
) -> None:

    now = datetime.datetime.now(JST)
    # include tomorrow's campaign
    if not (c.start - datetime.timedelta(days=1) <= now <= c.end):
        return

    _CAMPAIGNS.append(c)


class Plugin(auto_derby.Plugin):
    """Pick race by campaign."""

    def install(self) -> None:
        if not _CAMPAIGNS:
            app.log.text("no race campaign today")
            return

        for i in _CAMPAIGNS:
            app.log.text("race campaign: %s~%s %s" % (i.start, i.end, i.race_name))

        class Race(auto_derby.config.single_mode_race_class):
            def score(self, ctx: single_mode.Context) -> float:
                ret = super().score(ctx)
                if ret < 0:
                    return ret
                if any(i.match(ctx, self) for i in _CAMPAIGNS):
                    ret += 100
                return ret

        auto_derby.config.single_mode_race_class = Race


auto_derby.plugin.register(__name__, Plugin())


# 春のGⅠ記念ミッション　第２弾 宝塚記念

_start = datetime.datetime(2022, 6, 20, 4, 0, tzinfo=JST)
_end = datetime.datetime(2022, 6, 27, 3, 59, tzinfo=JST)
_add_campaign(OneTimeCampaign(_start, _end, "宝塚記念", order_lte=1))

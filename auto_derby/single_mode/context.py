# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, Iterator

from auto_derby.character import Character

if TYPE_CHECKING:
    from . import go_out

import logging
import os
from typing import Callable, List, Set, Text, Tuple, Type

import cast_unknown as cast
import cv2
import numpy as np
from PIL.Image import Image
from PIL.Image import fromarray as image_from_array

from .. import imagetools, mathtools, ocr, scenes, template, templates, texttools
from ..constants import Mood, TrainingType
from . import condition

_LOGGER = logging.getLogger(__name__)


class g:
    context_class: Type[Context]


def _year4_date_text(ctx: Context) -> Iterator[Text]:
    if ctx.scenario in (ctx.SCENARIO_URA, ctx.SCENARIO_AOHARU, ctx.SCENARIO_UNKNOWN):
        yield "ファイナルズ開催中"
    if ctx.scenario in (ctx.SCENARIO_CLIMAX, ctx.SCENARIO_UNKNOWN):
        yield "クライマックス開催中"


def _ocr_date(ctx: Context, img: Image) -> Tuple[int, int, int]:
    img = imagetools.resize(img, height=32)
    cv_img = np.asarray(img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    sharpened_img = imagetools.sharpen(cv_img)
    white_outline_img = imagetools.constant_color_key(
        sharpened_img,
        (255,),
        threshold=0.85,
    )
    white_outline_img = cv2.morphologyEx(
        white_outline_img,
        cv2.MORPH_CLOSE,
        np.ones((3, 3)),
    )
    bg_mask_img = imagetools.bg_mask_by_outline(white_outline_img)
    masked_img = cv2.copyTo(
        255 - imagetools.mix(cv_img, sharpened_img, 0.5), 255 - bg_mask_img
    )
    _, binary_img = cv2.threshold(masked_img, 200, 255, cv2.THRESH_BINARY)
    imagetools.fill_area(binary_img, (0,), size_lt=2)

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("sharpened_img", sharpened_img)
        cv2.imshow("white_outline_img", white_outline_img)
        cv2.imshow("bg_mask_img", bg_mask_img)
        cv2.imshow("masked_img", masked_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    text = ocr.text(image_from_array(binary_img))

    if texttools.compare(text, "ジュニア級デビュー前") > 0.8:
        return (1, 0, 0)
    for i in _year4_date_text(ctx):
        if texttools.compare(text, i) > 0.8:
            return (4, 0, 0)
    year_end = text.index("級") + 1
    month_end = year_end + text[year_end:].index("月") + 1
    year_text = text[:year_end]
    month_text = text[year_end:month_end]
    date_text = text[month_end:]

    year_dict = {"ジュニア級": 1, "クラシック級": 2, "シニア級": 3}
    year = year_dict[texttools.choose(year_text, year_dict.keys())]
    month = int(month_text[:-1])
    date = {"前半": 1, "後半": 2}[date_text]
    return (year, month, date)


def _recognize_vitality(img: Image) -> float:
    cv_img = np.asarray(img)

    def _is_empty(v: np.ndarray) -> bool:
        assert v.shape == (3,), v.shape
        return (
            imagetools.compare_color((118, 117, 118), (int(v[0]), int(v[1]), int(v[2])))
            > 0.99
        )

    return 1 - np.average(np.apply_along_axis(_is_empty, 1, cv_img[0, :]))


def _recognize_mood(rgb_color: Tuple[int, int, int]) -> Mood:
    if imagetools.compare_color((250, 68, 126), rgb_color) > 0.9:
        return Context.MOOD_VERY_GOOD
    if imagetools.compare_color((255, 124, 57), rgb_color) > 0.9:
        return Context.MOOD_GOOD
    if imagetools.compare_color((255, 162, 0), rgb_color) > 0.9:
        return Context.MOOD_NORMAL
    if imagetools.compare_color((16, 136, 247), rgb_color) > 0.9:
        return Context.MOOD_BAD
    if imagetools.compare_color((170, 81, 255), rgb_color) > 0.9:
        return Context.MOOD_VERY_BAD
    raise ValueError("_recognize_mood: unknown mood color: %s" % (rgb_color,))


def _recognize_fan_count(img: Image) -> int:
    cv_img = imagetools.cv_image(img.convert("L"))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 1), np.percentile(cv_img, 90)
    )
    _, binary_img = cv2.threshold(cv_img, 50, 255, cv2.THRESH_BINARY_INV)
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
    text = ocr.text(imagetools.pil_image(binary_img))
    return int(text.rstrip("人").replace(",", ""))


def _recognize_status(img: Image) -> Tuple[int, Text]:
    cv_img = imagetools.cv_image(imagetools.resize(img.convert("L"), height=64))
    cv_img = imagetools.level(
        cv_img, np.percentile(cv_img, 5), np.percentile(cv_img, 95)
    )
    cv_img = cv2.copyMakeBorder(cv_img, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=(255,))

    blurred_img = cv2.medianBlur(cv_img, 7)

    text_img = cv2.adaptiveThreshold(
        blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, -1
    )
    text_img = 255 - cast.instance(
        np.maximum(text_img, imagetools.border_flood_fill(text_img)), np.ndarray
    )
    text_img = cv2.medianBlur(text_img, 5)
    h = cv_img.shape[0]
    imagetools.fill_area(
        text_img, (0,), mode=cv2.RETR_LIST, size_lt=round(h * 0.2**2)
    )

    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("blurred_img", blurred_img)
        cv2.imshow("text_img", text_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    text = ocr.text(imagetools.pil_image(text_img))
    ret = Context.status_by_name(text)
    if ret != Context.STATUS_NONE:
        return ret

    raise ValueError("_recognize_status: unknown status: %s" % text)


def _recognize_property(img: Image) -> int:
    img = imagetools.resize(img, height=32)
    max_match = imagetools.constant_color_key(
        imagetools.cv_image(img),
        (210, 249, 255),
        threshold=0.95,
    )
    if np.average(max_match) > 5:
        return 1200

    cv_img = np.asarray(img.convert("L"))
    _, binary_img = cv2.threshold(cv_img, 160, 255, cv2.THRESH_BINARY_INV)
    imagetools.fill_area(binary_img, (0,), size_lt=3)
    if os.getenv("DEBUG") == __name__ + "[property]":
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("binary_img", binary_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    return int(ocr.text(imagetools.pil_image(binary_img)))


def _recognize_scenario(rp: mathtools.ResizeProxy, img: Image) -> Text:
    spec = (
        (
            template.Specification(
                templates.SINGLE_MODE_CLIMAX_GRADE_POINT_ICON, threshold=0.8
            ),
            Context.SCENARIO_CLIMAX,
        ),
        (
            template.Specification(
                templates.SINGLE_MODE_CLIMAX_RANK_POINT_ICON, threshold=0.8
            ),
            Context.SCENARIO_CLIMAX,
        ),
        (templates.SINGLE_MODE_AOHARU_CLASS_DETAIL_BUTTON, Context.SCENARIO_AOHARU),
        (templates.SINGLE_MODE_CLASS_DETAIL_BUTTON, Context.SCENARIO_URA),
    )
    ret = Context.SCENARIO_UNKNOWN
    for tmpl, scenario in spec:
        try:
            next(template.match(img, tmpl))
            ret = scenario
            break
        except StopIteration:
            pass
    _LOGGER.debug("_recognize_scenario: %s", ret)
    return ret


def _date_bbox(ctx: Context, rp: mathtools.ResizeProxy):
    if ctx.scenario == ctx.SCENARIO_AOHARU:
        return rp.vector4((125, 32, 278, 48), 540)
    if ctx.scenario == ctx.SCENARIO_CLIMAX:
        return rp.vector4((11, 32, 163, 48), 540)
    return rp.vector4((23, 66, 328, 98), 1080)


class Context:
    MOOD_VERY_BAD = Mood.VERY_BAD
    MOOD_BAD = Mood.BAD
    MOOD_NORMAL = Mood.NORMAL
    MOOD_GOOD = Mood.GOOD
    MOOD_VERY_GOOD = Mood.VERY_GOOD

    CONDITION_OVERWEIGHT = 4
    CONDITION_HEADACHE = 5
    CONDITION_SHARP = 7
    CONDITION_CHARM = 8

    STATUS_S = (8, "S")
    STATUS_A = (7, "A")
    STATUS_B = (6, "B")
    STATUS_C = (5, "C")
    STATUS_D = (4, "D")
    STATUS_E = (3, "E")
    STATUS_F = (2, "F")
    STATUS_G = (1, "G")
    STATUS_NONE: Tuple[int, Text] = (0, "")

    ALL_STATUSES = (
        STATUS_S,
        STATUS_A,
        STATUS_B,
        STATUS_C,
        STATUS_D,
        STATUS_E,
        STATUS_F,
        STATUS_G,
    )

    # master.mdb
    # SELECT text FROM text_data WHERE category=119;
    SCENARIO_UNKNOWN = ""
    SCENARIO_URA = "新設！　URAファイナルズ！！"
    SCENARIO_AOHARU = "アオハル杯～輝け、チームの絆～"
    SCENARIO_CLIMAX = "Make a new track!!  ～クライマックス開幕～"

    @staticmethod
    def new() -> Context:
        return g.context_class()

    def __init__(self) -> None:
        self.character = Character.UNKNOWN
        self.speed = 0
        self.stamina = 0
        self.power = 0
        self.guts = 0
        self.wisdom = 0
        # (year, month, half-month), 1-base
        self.date = (0, 0, 0)
        self.vitality = 0.0
        self.max_vitality = 100
        self.mood = Context.MOOD_NORMAL
        self.conditions: Set[int] = set()
        self.fan_count = 0
        self.is_after_winning = False

        self._extra_turn_count = 0
        self.target_fan_count = 0

        self.turf = Context.STATUS_NONE
        self.dart = Context.STATUS_NONE

        # Distance statuses
        # https://umamusume.cygames.jp/#/help?p=3
        # 短距離：1400m以下
        self.sprint = Context.STATUS_NONE
        # マイル：1401m～1800m
        self.mile = Context.STATUS_NONE
        # 中距離：1801m～2400m
        self.intermediate = Context.STATUS_NONE
        # 長距離：2401m以上
        self.long = Context.STATUS_NONE

        # Runing style status
        # https://umamusume.cygames.jp/#/help?p=3
        # 作戦には以下の4つがあります。
        # ・逃げ：スタート直後から先頭に立ち、そのまま最後まで逃げ切る作戦。
        self.lead = Context.STATUS_NONE
        # ・先行：なるべく前に付けて、先頭を狙っていく作戦。
        self.head = Context.STATUS_NONE
        # ・差し：後方につけ、レース後半に加速して先頭に立つ作戦。
        self.middle = Context.STATUS_NONE
        # ・追込：最後方に控え、最後に勝負をかける作戦。
        self.last = Context.STATUS_NONE

        self._next_turn_cb: List[Callable[[], None]] = []

        self.scene: scenes.Scene = scenes.UnknownScene()
        self.go_out_options: Tuple[go_out.Option, ...] = ()
        self.scenario = Context.SCENARIO_UNKNOWN

        self.grade_point = 0
        self.shop_coin = 0

        from . import training

        self.training_history = training.History()
        self.trainings: Tuple[training.Training, ...] = ()
        self.training_levels: Dict[TrainingType, int] = {}

        from . import race

        self.race_turns: Set[int] = set()
        self.race_history = race.History()

        from . import item

        self.items = item.ItemList()
        self.items_last_updated_turn = 0
        self.item_history = item.History()

    def target_grade_point(self) -> int:
        if self.date[1:] == (0, 0):
            return 0
        return (60, 200, 300, 0)[self.date[0] - 1]

    def next_turn(self) -> None:
        if self.date in ((1, 0, 0), (4, 0, 0)):
            self._extra_turn_count += 1
        else:
            self._extra_turn_count = 0

        while self._next_turn_cb:
            self._next_turn_cb.pop()()
        _LOGGER.info("next turn: %s", self)

    def defer_next_turn(self, cb: Callable[[], None]) -> None:
        self._next_turn_cb.append(cb)

    # TODO: refactor update_by_* to *Scene.recognize
    def update_by_command_scene(self, screenshot: Image) -> None:
        rp = mathtools.ResizeProxy(screenshot.width)
        if not self.scenario:
            self.scenario = _recognize_scenario(rp, screenshot)
        if not self.scenario:
            raise ValueError("unknown scenario")
        date_bbox = _date_bbox(self, rp)
        vitality_bbox = rp.vector4((148, 106, 327, 108), 466)

        _, detail_button_pos = next(
            template.match(screenshot, templates.SINGLE_MODE_CHARACTER_DETAIL_BUTTON)
        )
        base_y = detail_button_pos[1] + rp.vector(71, 466)
        t, b = base_y, base_y + rp.vector(19, 466)
        speed_bbox = (rp.vector(45, 466), t, rp.vector(90, 466), b)
        stamina_bbox = (rp.vector(125, 466), t, rp.vector(162, 466), b)
        power_bbox = (rp.vector(192, 466), t, rp.vector(234, 466), b)
        guts_bbox = (rp.vector(264, 466), t, rp.vector(308, 466), b)
        wisdom_bbox = (rp.vector(337, 466), t, rp.vector(381, 466), b)

        self.date = _ocr_date(self, screenshot.crop(date_bbox))

        self.vitality = _recognize_vitality(screenshot.crop(vitality_bbox))

        # mood_pos change when vitality increase
        for index, mood_pos in enumerate(
            (
                rp.vector2((395, 113), 466),
                rp.vector2((473, 133), 540),
            )
        ):
            mood_color = screenshot.getpixel(mood_pos)
            assert isinstance(mood_color, tuple), mood_color
            try:
                self.mood = _recognize_mood(
                    (mood_color[0], mood_color[1], mood_color[2])
                )
                break
            except ValueError:
                if index == 1:
                    raise

        self.speed = _recognize_property(screenshot.crop(speed_bbox))
        self.stamina = _recognize_property(screenshot.crop(stamina_bbox))
        self.power = _recognize_property(screenshot.crop(power_bbox))
        self.guts = _recognize_property(screenshot.crop(guts_bbox))
        self.wisdom = _recognize_property(screenshot.crop(wisdom_bbox))

    def update_by_class_detail(self, screenshot: Image) -> None:
        rp = mathtools.ResizeProxy(screenshot.width)
        winning_color_pos = rp.vector2((150, 470), 466)
        fan_count_bbox = rp.vector4((220, 523, 420, 540), 466)

        self.is_after_winning = (
            imagetools.compare_color(
                screenshot.getpixel(winning_color_pos),
                (244, 205, 52),
            )
            > 0.95
        )

        self.fan_count = _recognize_fan_count(screenshot.crop(fan_count_bbox))

    def update_by_character_detail(self, screenshot: Image) -> None:
        rp = mathtools.ResizeProxy(screenshot.width)
        grass_bbox = rp.vector4((158, 263, 173, 280), 466)
        dart_bbox = rp.vector4((244, 263, 258, 280), 466)

        sprint_bbox = rp.vector4((158, 289, 173, 305), 466)
        mile_bbox = rp.vector4((244, 289, 258, 305), 466)
        intermediate_bbox = rp.vector4((329, 289, 344, 305), 466)
        long_bbox = rp.vector4((414, 289, 430, 305), 466)

        lead_bbox = rp.vector4((158, 316, 173, 332), 466)
        head_bbox = rp.vector4((244, 316, 258, 332), 466)
        middle_bbox = rp.vector4((329, 316, 344, 332), 466)
        last_bbox = rp.vector4((414, 316, 430, 332), 466)

        conditions_bbox = rp.vector4((13, 506, 528, 832), 540)

        self.turf = _recognize_status(screenshot.crop(grass_bbox))
        self.dart = _recognize_status(screenshot.crop(dart_bbox))

        self.sprint = _recognize_status(screenshot.crop(sprint_bbox))
        self.mile = _recognize_status(screenshot.crop(mile_bbox))
        self.intermediate = _recognize_status(screenshot.crop(intermediate_bbox))
        self.long = _recognize_status(screenshot.crop(long_bbox))

        self.lead = _recognize_status(screenshot.crop(lead_bbox))
        self.head = _recognize_status(screenshot.crop(head_bbox))
        self.middle = _recognize_status(screenshot.crop(middle_bbox))
        self.last = _recognize_status(screenshot.crop(last_bbox))

        self.conditions = _recognize_conditions(screenshot.crop(conditions_bbox))

    def __str__(self):
        msg = ""
        if self.scenario == Context.SCENARIO_CLIMAX:
            msg += f",pt={self.grade_point},coin={self.shop_coin},items={self.items.quantity()}"
        if self.go_out_options:
            msg += ",go_out="
            msg += " ".join(
                (
                    f"{i.current_event_count}/{i.total_event_count}"
                    for i in self.go_out_options
                )
            )
        if self.conditions:
            msg += ",cond="
            msg += " ".join((condition.get(i).name for i in self.conditions))
        return (
            "Context<"
            f"scenario={self.scenario},"
            f"turn={self.turn_count_v2()},"
            f"mood={self.mood},"
            f"vit={self.vitality:.3f},"
            f"spd={self.speed},"
            f"sta={self.stamina},"
            f"pow={self.power},"
            f"gut={self.guts},"
            f"wis={self.wisdom},"
            f"fan={self.fan_count},"
            f"ground={''.join(i[1] for i in (self.turf, self.dart))},"
            f"distance={''.join(i[1] for i in (self.sprint, self.mile, self.intermediate, self.long))},"
            f"style={''.join(i[1] for i in (self.last, self.middle, self.head, self.lead))}"
            f"{msg}"
            ">"
        )

    @property
    def condition(self) -> int:
        import warnings

        warnings.warn(
            "Context.condition is Depreacted, use conditions (with `s`) instead.",
            DeprecationWarning,
        )
        ret = 0
        if self.CONDITION_HEADACHE in self.conditions:
            ret |= 1 << 0
        if self.CONDITION_OVERWEIGHT in self.conditions:
            ret |= 1 << 1
        return ret

    @condition.setter
    def condition(self, v: int):
        import warnings

        warnings.warn(
            "Context.condition is Depreacted, use conditions (with `s`) instead.",
            DeprecationWarning,
        )
        self.conditions.clear()
        if 1 << 0 & v:
            self.conditions.add(self.CONDITION_HEADACHE)
        if 1 << 1 & v:
            self.conditions.add(self.CONDITION_OVERWEIGHT)

    def turn_count(self) -> int:
        import warnings

        warnings.warn(
            "use turn_count_v2 instead, date (2,1,1) should be turn 25, not 24.",
            DeprecationWarning,
        )
        if self.date == (1, 0, 0):
            return self._extra_turn_count
        if self.date == (4, 0, 0):
            return self._extra_turn_count + 24 * 3
        return (self.date[0] - 1) * 24 + (self.date[1] - 1) * 2 + (self.date[2] - 1)

    def turn_count_v2(self) -> int:
        if self.date == (1, 0, 0):
            return self._extra_turn_count
        if self.date == (4, 0, 0):
            return self._extra_turn_count + 24 * 3
        return (self.date[0] - 1) * 24 + (self.date[1] - 1) * 2 + self.date[2]

    def total_turn_count(self) -> int:
        return 24 * 3 + 6

    @staticmethod
    def date_from_turn_count_v2(turn_count: int) -> Tuple[int, int, int]:
        c = turn_count - 1
        year = c // 24 + 1
        c %= 24
        month = c // 2 + 1
        c %= 2
        half = c + 1
        return (year, month, half)

    def continuous_race_count(self) -> int:
        ret = 1
        turn = self.turn_count() - 1
        while turn in self.race_turns:
            ret += 1
            turn -= 1
        return ret

    @property
    def is_summer_camp(self) -> bool:
        return self.date[0] in (2, 3) and self.date[1:] in (
            (7, 1),
            (7, 2),
            (8, 1),
            (8, 2),
        )

    def expected_score(self) -> float:
        import warnings

        warnings.warn(
            "expected score is deprecated, use rest/go-out command score instead",
            DeprecationWarning,
        )

        expected_score = 15 + self.turn_count() * 10 / 24

        can_heal_condition = not self.is_summer_camp
        if self.vitality > 0.5:
            expected_score *= 0.5
        if self.turn_count() >= self.total_turn_count() - 2:
            expected_score *= 0.1
        if self.date[1:] in ((6, 1),) and self.vitality < 0.8:
            expected_score += 10
        if self.date[1:] in ((6, 2),) and self.vitality < 0.9:
            expected_score += 20
        if self.is_summer_camp and self.vitality < 0.8:
            expected_score += 10
        if self.date in ((4, 0, 0)):
            expected_score -= 20
        if can_heal_condition:
            expected_score += (
                len(
                    set(
                        (
                            Context.CONDITION_HEADACHE,
                            Context.CONDITION_OVERWEIGHT,
                        )
                    ).intersection(self.conditions)
                )
                * 20
            )
        expected_score += (self.MOOD_VERY_GOOD[0] - self.mood[0]) * 40 * 3

        return expected_score

    def to_dict(self) -> Dict[Text, Any]:
        d = {
            "date": self.date,
            "mood": self.mood.name,
            "scenario": self.scenario,
            "vitality": self.vitality,
            "maxVitality": self.max_vitality,
            "speed": self.speed,
            "stamina": self.stamina,
            "power": self.power,
            "guts": self.guts,
            "wisdom": self.wisdom,
            "fanCount": self.fan_count,
            "turf": self.turf[1],
            "dart": self.dart[1],
            "sprint": self.sprint[1],
            "mile": self.mile[1],
            "intermediate": self.intermediate[1],
            "long": self.long[1],
            "last": self.last[1],
            "middle": self.middle[1],
            "head": self.head[1],
            "lead": self.lead[1],
            "conditions": list(self.conditions),
        }
        if self.scenario == self.SCENARIO_CLIMAX:
            d["gradePoint"] = self.grade_point
            d["shopCoin"] = self.shop_coin
        return d

    def clone(self):
        return deepcopy(self)

    @classmethod
    def status_by_name(cls, name: Text) -> Tuple[int, Text]:
        for i in cls.ALL_STATUSES:
            if i[1] == name:
                return i
        return cls.STATUS_NONE

    @classmethod
    def from_dict(cls, data: Dict[Text, Any]) -> Context:

        ret = cls()
        ret.speed = data["speed"]
        ret.stamina = data["stamina"]
        ret.power = data["power"]
        ret.guts = data["guts"]
        ret.wisdom = data["wisdom"]
        ret.date = tuple(data["date"])
        ret.vitality = data["vitality"]
        ret.max_vitality = data["maxVitality"]
        mood_data = data["mood"]
        if isinstance(mood_data, list):
            ret.mood = next(
                i for i in Mood if [i.training_rate, i.race_rate] == data["mood"]
            )
        else:
            ret.mood = Mood[mood_data]
        if "condition" in data:
            ret.condition = data["condition"]
        else:
            ret.conditions = set(data["conditions"])
        ret.fan_count = data["fanCount"]
        ret.turf = cls.status_by_name(data["turf"])
        ret.dart = cls.status_by_name(data["dart"])
        ret.sprint = cls.status_by_name(data["sprint"])
        ret.mile = cls.status_by_name(data["mile"])
        ret.intermediate = cls.status_by_name(data["intermediate"])
        ret.long = cls.status_by_name(data["long"])
        ret.lead = cls.status_by_name(data["lead"])
        ret.head = cls.status_by_name(data["head"])
        ret.middle = cls.status_by_name(data["middle"])
        ret.last = cls.status_by_name(data["last"])
        ret.scenario = data["scenario"]
        ret.grade_point = data.get("gradePoint", 0)
        ret.shop_coin = data.get("shopCoin", 0)

        return ret


g.context_class = Context

# TODO: use label match
_CONDITION_TEMPLATES = {
    templates.SINGLE_MODE_CONDITION_HEADACHE: Context.CONDITION_HEADACHE,
    templates.SINGLE_MODE_CONDITION_OVERWEIGHT: Context.CONDITION_OVERWEIGHT,
    templates.SINGLE_MODE_CONDITION_CHARM: Context.CONDITION_CHARM,
    templates.SINGLE_MODE_CONDITION_SHARP: Context.CONDITION_SHARP,
}


def _recognize_conditions(img: Image) -> Set[int]:
    ret: Set[int] = set()
    for tmpl, _ in template.match(
        img,
        *_CONDITION_TEMPLATES.keys(),
    ):
        ret.add(_CONDITION_TEMPLATES[tmpl.name])
    return ret

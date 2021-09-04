# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

from PIL.Image import Image
from auto_derby import constants, template

from typing import Any, Dict, Iterator, Text, Tuple

from ... import action, templates, mathtools
from ...scenes import Scene
from ..scene import Scene, SceneHolder


def _recognize_predictions(
    screenshot: Image,
) -> Iterator[Tuple[constants.RaceType, constants.RacePrediction]]:
    rp = mathtools.ResizeProxy(screenshot.width)
    bbox_list = (
        (constants.RaceType.SPRINT, rp.vector4((31, 505, 113, 533), 540)),
        (constants.RaceType.MILE, rp.vector4((136, 505, 199, 533), 540)),
        (constants.RaceType.INTERMEDIATE, rp.vector4((230, 505, 309, 533), 540)),
        (constants.RaceType.LONG, rp.vector4((331, 505, 405, 533), 540)),
        (constants.RaceType.DART, rp.vector4((429, 505, 505, 533), 540)),
    )

    predition_templates = (
        (constants.RacePrediction.HONNMEI, templates.PREDICTION_DOUBLE_CIRCLE),
        (constants.RacePrediction.TAIKOU, templates.PREDICTION_CIRCLE_OUTLINE),
        # TODO: add template for this
        # (constants.RacePrediction.TANNANA, templates.PREDICTION_TRIANGLE),
        (constants.RacePrediction.RENNSHITA, templates.PREDICTION_TRIANGLE_OUTLINE),
    )

    for t, bbox in bbox_list:
        img = screenshot.crop(bbox)
        for p, tmpl in predition_templates:
            try:
                next(
                    template.match(
                        img,
                        tmpl,
                    )
                )
                yield t, p
            except StopIteration:
                continue


class AoharuBattleConfirmScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.predictions: Dict[constants.RaceType, constants.RacePrediction] = {}

    def to_dict(self) -> Dict[Text, Any]:
        return {
            "predictions": self.predictions,
        }

    @classmethod
    def name(cls):
        return "single-mode-aoharu-battle-confirm"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        action.wait_image(templates.SINGLE_MODE_AOHARU_BATTLE_CONFIRM_TITLE)
        return cls()

    def recognize_predictions(self) -> None:
        self.predictions = dict(_recognize_predictions(template.screenshot()))

# -*- coding=UTF-8 -*-
# pyright: strict

from __future__ import annotations

import os
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL.Image import Image

from ... import action, imagetools, mathtools, template, templates
from ..scene import Scene, SceneHolder
from ..unknown import UnknownScene


def _has_granted_reward(img: Image) -> bool:
    cv_img = imagetools.cv_image(imagetools.resize(img, height=25).convert("L"))
    blur_img = cv2.GaussianBlur(cv_img, (5, 9), 1)
    diff_img = blur_img - cv_img
    if os.getenv("DEBUG") == __name__:
        cv2.imshow("cv_img", cv_img)
        cv2.imshow("blur_img", blur_img)
        cv2.imshow("diff_img", diff_img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    return np.average(diff_img) > 100


def _iter_reward_bbox(rp: mathtools.ResizeProxy):
    for t in (330, 533, 735):
        yield rp.vector4((400, t, 500, t + 25), 540)


class CompetitorMenuScene(Scene):
    @classmethod
    def name(cls):
        return "paddock"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        action.wait_image_stable(templates.TEAM_RACE_CHOOSE_COMPETITOR)
        return cls()

    def locate_granted_reward(self) -> Optional[Tuple[int, int]]:
        rp = action.resize_proxy()
        screenshot = template.screenshot()
        for bbox in _iter_reward_bbox(rp):
            if _has_granted_reward(screenshot.crop(bbox)):
                return (bbox[0], bbox[1])

    def choose(self, ctx: SceneHolder, index: int) -> None:
        """choose competitor by index, topmost option is 0."""
        rp = action.resize_proxy()
        for i, bbox in enumerate(_iter_reward_bbox(rp)):
            if i == index:
                action.tap((bbox[0], bbox[1]))
                UnknownScene.enter(ctx)
                return
        raise IndexError(index)

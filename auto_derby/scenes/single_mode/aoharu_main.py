# pyright: strict

from __future__ import annotations

from auto_derby import imagetools


from ... import action, templates, app
from ...scenes import Scene
from ..scene import Scene, SceneHolder


class AoharuMainScene(Scene):
    def __init__(self) -> None:
        super().__init__()
        self.is_final = False

    @classmethod
    def name(cls):
        return "single-mode-aoharu-main"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        if ctx.scene.name() == "single-mode-aoharu-competitor":
            action.wait_tap_image(templates.RETURN_BUTTON)
        action.wait_image(templates.SINGLE_MODE_AOHARU_FORMAL_RACE_BANNER)
        return cls()

    def go_race(self) -> None:
        rp = action.resize_proxy()
        app.device.tap(rp.vector4(imagetools.rect_from_bbox((195, 786, 343, 842)), 540))

    def recognize(self) -> None:
        self.is_final = (
            action.count_image(templates.SINGLE_MODE_AOHARU_FINAL_BANNER) > 0
        )

# pyright: strict

from __future__ import annotations


from ... import action, templates
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
        action.tap(rp.vector2((265, 805), 540))

    def recognize(self) -> None:
        self.is_final = (
            action.count_image(templates.SINGLE_MODE_AOHARU_FINAL_BANNER) > 0
        )

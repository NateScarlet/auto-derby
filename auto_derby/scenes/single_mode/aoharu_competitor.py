# pyright: strict

from __future__ import annotations


from ... import action, templates
from ...scenes import Scene
from ..scene import Scene, SceneHolder


class AoharuCompetitorScene(Scene):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def name(cls):
        return "single-mode-aoharu-competitor"

    @classmethod
    def _enter(cls, ctx: SceneHolder) -> Scene:
        if ctx.scene.name() == "single-mode-aoharu-battle-confirm":
            action.wait_tap_image(templates.CANCEL_BUTTON)
        action.wait_image(templates.SINGLE_MODE_AOHARU_CHOOSE_COMPETITOR)
        return cls()

    def choose_competitor(self, index: int) -> None:
        rp = action.resize_proxy()
        pos = (
            rp.vector2((180, 225), 540),
            rp.vector2((180, 410), 540),
            rp.vector2((180, 600), 540),
        )[index]
        action.tap(pos)

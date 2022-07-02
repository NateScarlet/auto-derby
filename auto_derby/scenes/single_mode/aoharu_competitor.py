# pyright: strict

from __future__ import annotations
from ... import imagetools, template


from ... import action, templates, app
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
        action.wait_image(
            template.Specification(
                templates.SINGLE_MODE_AOHARU_CHOOSE_COMPETITOR,
                threshold=0.8,
            ),
        )
        return cls()

    def choose_competitor(self, index: int) -> None:
        rp = action.resize_proxy()
        rect = (
            rp.vector4(imagetools.rect_from_bbox((25, 151, 500, 292)), 540),
            rp.vector4(imagetools.rect_from_bbox((25, 410, 500, 512)), 540),
            rp.vector4(imagetools.rect_from_bbox((25, 549, 500, 714)), 540),
        )[index]
        app.device.tap(rect)

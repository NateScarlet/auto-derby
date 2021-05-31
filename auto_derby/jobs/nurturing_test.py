from .nurturing import Context

from pathlib import Path
import PIL.Image


def test_context_update_by_command_scene_issue7():
    img = PIL.Image.open(Path(__file__).parent /
                         "test_data" / "nurturing_comand_scene_issue7.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 0, 0)
    assert ctx.vitality == 1
    assert ctx.speed == 158
    assert ctx.stamina == 190
    assert ctx.power == 67
    assert ctx.perservance == 95
    assert ctx.intelligence == 90

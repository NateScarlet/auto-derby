import PIL.Image
from . import race, _test
from .context import Context


def test_find_by_race_detail_image():

    img = PIL.Image.open(_test.DATA_PATH / "race_detail.png").convert("RGB")
    ctx = Context()
    ctx.date = (2, 3, 1)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "弥生賞"

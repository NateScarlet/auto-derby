import PIL.Image
from . import race, _test
from .context import Context


def test_find_by_race_detail_image():

    img = PIL.Image.open(_test.DATA_PATH / "race_detail.png").convert("RGB")
    ctx = Context()
    ctx.date = (2, 3, 1)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "弥生賞", race1.name


def test_find_by_race_detail_image_2():

    img = PIL.Image.open(_test.DATA_PATH / "race_detail_2.png").convert("RGB")
    ctx = Context()
    ctx.date = (2, 5, 1)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "NHKマイルカップ", race1.name


def test_find_by_race_detail_image_3():

    img = PIL.Image.open(_test.DATA_PATH / "race_detail_3.png").convert("RGB")
    ctx = Context()
    ctx.date = (2, 3, 1)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "昇竜ステークス", race1.name


def test_find_by_race_detail_image_4():

    img = PIL.Image.open(_test.DATA_PATH / "race_detail_4.png").convert("RGB")
    ctx = Context()
    ctx.date = (3, 2, 2)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "ダイヤモンドステークス", race1.name


def test_find_by_race_detail_image_5():

    img = PIL.Image.open(_test.DATA_PATH / "race_detail_5.png").convert("RGB")
    ctx = Context()
    ctx.date = (2, 10, 2)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "菊花賞", race1.name

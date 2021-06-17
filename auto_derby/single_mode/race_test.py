import PIL.Image
from . import race, _test
from .context import Context


def test_find_by_race_detail_image():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (2, 3, 1)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "弥生賞", race1.name
    assert race1.stadium == "中山", race1.stadium


def test_find_by_race_detail_image_2():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_2.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (2, 5, 1)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "NHKマイルカップ", race1.name
    assert race1.stadium == "東京", race1.stadium


def test_find_by_race_detail_image_3():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_3.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (2, 3, 1)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "昇竜ステークス", race1.name
    assert race1.stadium == "中京", race1.stadium


def test_find_by_race_detail_image_4():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_4.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (3, 2, 2)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "ダイヤモンドステークス", race1.name
    assert race1.stadium == "東京", race1.stadium


def test_find_by_race_detail_image_5():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_5.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (2, 10, 2)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "菊花賞", race1.name
    assert race1.stadium == "京都", race1.stadium


def test_find_by_race_detail_image_6():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_6.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (3, 6, 2)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "宝塚記念", race1.name
    assert race1.stadium == "阪神", race1.stadium


def test_find_by_race_detail_image_7():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_7.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (4, 0, 0)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "URAファイナルズ準決勝", race1.name
    assert race1.stadium == "阪神", race1.stadium


def test_find_by_race_detail_image_8():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_8.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (1, 0, 0)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "ジュニア級メイクデビュー", race1.name
    assert race1.stadium == "札幌", race1.stadium


def test_find_by_race_detail_image_9():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_9.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (1, 10, 1)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "紫菊賞", race1.name
    assert race1.stadium == "京都", race1.stadium


def test_find_by_race_detail_image_10():
    img = PIL.Image.open(_test.DATA_PATH / "race_detail_10.png").convert("RGB")
    ctx = Context.new()
    ctx.date = (1, 9, 1)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "小倉ジュニアステークス", race1.name
    assert race1.stadium == "小倉", race1.stadium


def test_find_by_race_detail_image_issue31():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_issue31.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (2, 5, 2)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "東京優駿（日本ダービー）", race1.name
    assert race1.stadium == "東京", race1.stadium


def test_find_by_race_detail_image_issue49():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_issue49.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (1, 8, 1)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "コスモス賞", race1.name
    assert race1.stadium == "札幌", race1.stadium


def test_find_by_race_detail_image_issue54():
    img = (
        PIL.Image.open(_test.DATA_PATH / "race_detail_issue54.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.date = (2, 10, 2)
    race1 = race.find_by_race_detail_image(ctx, img)

    assert race1.name == "ルミエールオータムダッシュ", race1.name
    assert race1.stadium == "新潟", race1.stadium

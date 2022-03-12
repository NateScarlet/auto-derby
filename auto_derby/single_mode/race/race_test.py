from .. import race
from ... import _test
from ..context import Context


def test_find_by_race_detail_image():
    img, _ = _test.use_screenshot("single_mode/race_detail.png")
    ctx = Context.new()
    ctx.date = (2, 3, 1)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "弥生賞", race1.name
    assert race1.stadium == "中山", race1.stadium


def test_find_by_race_detail_image_2():
    img, _ = _test.use_screenshot("single_mode/race_detail_2.png")
    ctx = Context.new()
    ctx.date = (2, 5, 1)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "NHKマイルカップ", race1.name
    assert race1.stadium == "東京", race1.stadium


def test_find_by_race_detail_image_3():
    img, _ = _test.use_screenshot("single_mode/race_detail_3.png")
    ctx = Context.new()
    ctx.date = (2, 3, 1)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "昇竜ステークス", race1.name
    assert race1.stadium == "中京", race1.stadium


def test_find_by_race_detail_image_4():
    img, _ = _test.use_screenshot("single_mode/race_detail_4.png")
    ctx = Context.new()
    ctx.date = (3, 2, 2)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "ダイヤモンドステークス", race1.name
    assert race1.stadium == "東京", race1.stadium


def test_find_by_race_detail_image_5():
    img, _ = _test.use_screenshot("single_mode/race_detail_5.png")
    ctx = Context.new()
    ctx.date = (2, 10, 2)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "菊花賞", race1.name
    assert race1.stadium == "京都", race1.stadium


def test_find_by_race_detail_image_6():
    img, _ = _test.use_screenshot("single_mode/race_detail_6.png")
    ctx = Context.new()
    ctx.date = (3, 6, 2)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "宝塚記念", race1.name
    assert race1.stadium == "阪神", race1.stadium


def test_find_by_race_detail_image_7():
    img, _ = _test.use_screenshot("single_mode/race_detail_7.png")
    ctx = Context.new()
    ctx.date = (4, 0, 0)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "URAファイナルズ準決勝", race1.name
    assert race1.stadium == "阪神", race1.stadium


def test_find_by_race_detail_image_8():
    img, _ = _test.use_screenshot("single_mode/race_detail_8.png")
    ctx = Context.new()
    ctx.date = (1, 0, 0)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "ジュニア級メイクデビュー", race1.name
    assert race1.stadium == "札幌", race1.stadium


def test_find_by_race_detail_image_9():
    img, _ = _test.use_screenshot("single_mode/race_detail_9.png")
    ctx = Context.new()
    ctx.date = (1, 10, 1)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "紫菊賞", race1.name
    assert race1.stadium == "京都", race1.stadium


def test_find_by_race_detail_image_10():
    img, _ = _test.use_screenshot("single_mode/race_detail_10.png")
    ctx = Context.new()
    ctx.date = (1, 9, 1)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "小倉ジュニアステークス", race1.name


def test_find_by_race_detail_image_11():
    img, _ = _test.use_screenshot("single_mode/race_detail_11.png")
    ctx = Context.new()
    ctx.date = (2, 4, 1)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "忘れな草賞", race1.name
    assert race1.stadium == "阪神", race1.stadium
    assert race1.characters == set(), race1.characters


def test_find_by_race_detail_image_issue31():
    img, _ = _test.use_screenshot("single_mode/race_detail_issue31.png")
    ctx = Context.new()
    ctx.date = (2, 5, 2)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "東京優駿（日本ダービー）", race1.name
    assert race1.stadium == "東京", race1.stadium


def test_find_by_race_detail_image_issue49():
    img, _ = _test.use_screenshot("single_mode/race_detail_issue49.png")
    ctx = Context.new()
    ctx.date = (1, 8, 1)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "コスモス賞", race1.name
    assert race1.stadium == "札幌", race1.stadium


def test_find_by_race_detail_image_issue54():
    img, _ = _test.use_screenshot("single_mode/race_detail_issue54.png")
    ctx = Context.new()
    ctx.date = (2, 10, 2)
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "ルミエールオータムダッシュ", race1.name
    assert race1.stadium == "新潟", race1.stadium


def test_find_by_race_detail_image_issue58():
    ctx = Context.new()
    ctx.date = (3, 6, 2)
    img, _ = _test.use_screenshot("single_mode/race_detail_issue58.png")
    race1 = race.find_by_race_detail_image(ctx, img)
    _test.snapshot_match(race1)

    assert race1.name == "宝塚記念", race1.name
    assert race1.stadium == "京都", race1.stadium
    assert race1.characters == {"メジロマックイーン", "メジロライアン", "ライスシャワー"}, race1.characters


def test_find_by_race_menu_image():
    ctx = Context.new()
    ctx.date = (1, 6, 2)
    img, _ = _test.use_screenshot("single_mode/race_menu.png")
    (res1,) = race.find_by_race_menu_image(ctx, img)
    race1, pos1 = res1

    assert pos1 == (203, 586), pos1
    assert race1.name == "ジュニア級メイクデビュー", race1.name
    assert race1.stadium == "札幌", race1.stadium
    assert race1.characters == {"ゴールドシップ", "エアグルーヴ", "ナリタタイシン"}, race1.characters


def test_find_by_race_menu_image_2():
    ctx = Context.new()
    ctx.date = (1, 10, 2)
    img, _ = _test.use_screenshot("single_mode/race_menu_2.png")
    res1, res2 = race.find_by_race_menu_image(ctx, img)
    race1, pos1 = res1
    race2, pos2 = res2

    assert pos1 == (203, 586), pos1
    assert race1.name == "アルテミスステークス", race1.name
    assert race1.stadium == "東京", race1.stadium
    assert race1.characters == set(), race1.characters

    assert pos2 == (203, 701), pos2
    assert race2.name == "アイビーステークス", race2.name
    assert race2.stadium == "東京", race2.stadium
    assert race2.characters == set(), race2.characters


def test_find_by_race_menu_image_3():
    ctx = Context.new()
    ctx.date = (1, 10, 2)
    img, _ = _test.use_screenshot("single_mode/race_menu_3.png")
    (res1,) = race.find_by_race_menu_image(ctx, img)
    race1, pos1 = res1

    assert pos1 == (203, 646), pos1
    assert race1.name == "萩ステークス", race1.name
    assert race1.stadium == "京都", race1.stadium
    assert race1.characters == set(), race1.characters


def test_find_by_race_menu_image_4():
    ctx = Context.new()
    ctx.date = (1, 10, 2)
    img, _ = _test.use_screenshot("single_mode/race_menu_4.png")
    res1, res2 = sorted(race.find_by_race_menu_image(ctx, img), key=lambda x: x[1][1])
    race1, pos1 = res1
    race2, pos2 = res2

    assert pos1 == (203, 585), pos1
    assert race1.name == "萩ステークス", race1.name
    assert race1.stadium == "京都", race1.stadium
    assert race1.characters == set(), race1.characters

    assert pos2 == (203, 700), pos2
    assert race2.name == "なでしこ賞", race2.name
    assert race2.stadium == "京都", race2.stadium
    assert race2.characters == set(), race2.characters


def test_find_by_race_menu_image_5():
    ctx = Context.new()
    ctx.date = (4, 0, 0)
    img, _ = _test.use_screenshot("single_mode/race_menu_5.png")
    res = sorted(race.find_by_race_menu_image(ctx, img), key=lambda x: x[1][1])
    _test.snapshot_match(res)


def test_find_by_race_menu_image_6():
    ctx = Context.new()
    ctx.date = (1, 11, 2)
    img, _ = _test.use_screenshot("single_mode/race_menu_6.png")
    res1, res2, res3 = sorted(
        race.find_by_race_menu_image(ctx, img),
        key=lambda x: (x[1][1], x[0].name),
    )
    race1, pos1 = res1
    # 2 race has exact same spec
    race2, pos2 = res2
    race3, pos3 = res3

    assert pos1 == (203, 595), pos1
    assert race1.name == "もちの木賞", race1.name
    assert race1.stadium == "京都", race1.stadium
    assert race1.characters == set(), race1.characters

    assert pos2 == (203, 710), pos2
    assert race2.name == "ベゴニア賞", race2.name
    assert race2.stadium == "東京", race2.stadium
    assert race2.characters == set(), race2.characters

    assert pos3 == (203, 710), pos3
    assert race3.name == "赤松賞", race3.name
    assert race3.stadium == "東京", race3.stadium
    assert race3.characters == set(), race3.characters


def test_find_by_race_menu_image_7():
    ctx = Context.new()
    ctx.date = (3, 4, 2)
    img, _ = _test.use_screenshot("single_mode/race_menu_7.png")
    res = sorted(race.find_by_race_menu_image(ctx, img), key=lambda x: x[1][1])
    _test.snapshot_match(res)


def test_find_by_race_menu_image_8():
    ctx = Context.new()
    ctx.date = (1, 0, 0)
    ctx.scenario = ctx.SCENARIO_CLIMAX
    img, _ = _test.use_screenshot("single_mode/race_menu_8.png")
    res = sorted(race.find_by_race_menu_image(ctx, img), key=lambda x: x[1][1])
    _test.snapshot_match(res)


def test_find_by_race_menu_image_9():
    ctx = Context.new()
    ctx.date = (1, 8, 2)
    ctx.scenario = ctx.SCENARIO_CLIMAX
    img, _ = _test.use_screenshot("single_mode/race_menu_9.png")
    res = sorted(race.find_by_race_menu_image(ctx, img), key=lambda x: x[1][1])
    _test.snapshot_match(res)


def test_find_by_race_menu_image_10():
    ctx = Context.new()
    ctx.date = (3, 10, 2)
    ctx.scenario = ctx.SCENARIO_CLIMAX
    img, _ = _test.use_screenshot("single_mode/race_menu_10.png")
    res = sorted(race.find_by_race_menu_image(ctx, img), key=lambda x: x[1][1])
    _test.snapshot_match(res)


def test_find_by_race_menu_image_issue112():
    ctx = Context.new()
    ctx.date = (1, 12, 1)
    img, _ = _test.use_screenshot("single_mode/race_menu_issue112.png")
    res1, res2 = sorted(race.find_by_race_menu_image(ctx, img), key=lambda x: x[1][1])
    race1, pos1 = res1
    race2, pos2 = res2

    assert pos1 == (203, 586), pos1
    assert race1.name == "さざんか賞", race1.name
    assert race1.stadium == "阪神", race1.stadium
    assert race1.characters == set(), race1.characters

    assert pos2 == (203, 701), pos2
    assert race2.name == "朝日杯フューチュリティステークス", race2.name
    assert race2.stadium == "阪神", race2.stadium
    assert race2.characters == set(), race2.characters


def test_find_by_race_menu_image_issue216():
    ctx = Context.new()
    ctx.date = (1, 12, 1)
    img, _ = _test.use_screenshot("single_mode/race_menu_issue216.png")
    res = sorted(race.find_by_race_menu_image(ctx, img), key=lambda x: x[1][1])
    _test.snapshot_match(res)


def test_find_by_race_menu_image_issue217():
    ctx = Context.new()
    ctx.date = (4, 0, 0)
    img, _ = _test.use_screenshot("single_mode/race_menu_issue217.png")
    res = sorted(race.find_by_race_menu_image(ctx, img), key=lambda x: x[1][1])
    _test.snapshot_match(res)

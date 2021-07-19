from .context import Context

from pathlib import Path
import PIL.Image

from . import _test

_TEST_DATA_PATH = Path(__file__).parent / "test_data"


def test_update_by_command_scene():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "command_scene.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 12, 2), ctx.date
    assert round(ctx.vitality, 2) == 0.92, ctx.vitality
    assert ctx.speed == 281, ctx.speed
    assert ctx.stamina == 217, ctx.stamina
    assert ctx.power == 210, ctx.power
    assert ctx.guts == 187, ctx.guts
    assert ctx.wisdom == 266, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_2():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "command_scene_2.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    assert ctx.date == (2, 1, 1), ctx.date
    assert round(ctx.vitality, 2) == 0.92, ctx.vitality
    assert ctx.speed == 281, ctx.speed
    assert ctx.stamina == 217, ctx.stamina
    assert ctx.power == 210, ctx.power
    assert ctx.guts == 198, ctx.guts
    assert ctx.wisdom == 266, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_3():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "command_scene_3.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    assert ctx.date == (3, 1, 1), ctx.date
    assert round(ctx.vitality, 2) == 1, ctx.vitality
    assert ctx.speed == 589, ctx.speed
    assert ctx.stamina == 375, ctx.stamina
    assert ctx.power == 461, ctx.power
    assert ctx.guts == 263, ctx.guts
    assert ctx.wisdom == 386, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_4():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "command_scene_4.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    assert ctx.date == (2, 4, 1), ctx.date
    assert round(ctx.vitality, 2) == 0.95, ctx.vitality
    assert ctx.speed == 357, ctx.speed
    assert ctx.stamina == 279, ctx.stamina
    assert ctx.power == 275, ctx.power
    assert ctx.guts == 216, ctx.guts
    assert ctx.wisdom == 250, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_5():
    with _test.screenshot("command_scene_5.png") as img:
        ctx = Context.new()
        ctx.update_by_command_scene(img)
        assert ctx.date == (3, 3, 1), ctx.date
        assert round(ctx.vitality, 2) == 0.74, ctx.vitality
        assert ctx.speed == 568, ctx.speed
        assert ctx.stamina == 368, ctx.stamina
        assert ctx.power == 341, ctx.power
        assert ctx.guts == 307, ctx.guts
        assert ctx.wisdom == 329, ctx.wisdom
        assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_6():
    with _test.screenshot("command_scene_6.png") as img:
        ctx = Context.new()
        ctx.update_by_command_scene(img)
        assert ctx.date == (2, 10, 1), ctx.date
        assert round(ctx.vitality, 2) == 0.46, ctx.vitality
        assert ctx.speed == 510, ctx.speed
        assert ctx.stamina == 317, ctx.stamina
        assert ctx.power == 351, ctx.power
        assert ctx.guts == 298, ctx.guts
        assert ctx.wisdom == 314, ctx.wisdom
        assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_7():
    with _test.screenshot("command_scene_7.png") as img:
        ctx = Context.new()
        ctx.update_by_command_scene(img)
        assert ctx.date == (2, 12, 2), ctx.date
        assert round(ctx.vitality, 2) == 0.33, ctx.vitality
        assert ctx.speed == 615, ctx.speed
        assert ctx.stamina == 316, ctx.stamina
        assert ctx.power == 459, ctx.power
        assert ctx.guts == 251, ctx.guts
        assert ctx.wisdom == 382, ctx.wisdom
        assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_issue7():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "command_scene_issue7.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 0, 0)
    assert round(ctx.vitality, 2) == 1
    assert ctx.speed == 158
    assert ctx.stamina == 190
    assert ctx.power == 67
    assert ctx.guts == 95
    assert ctx.wisdom == 90
    assert ctx.mood == ctx.MOOD_NORMAL


def test_update_by_command_scene_issue12():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "command_scene_issue12.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 12, 2), ctx.date
    assert round(ctx.vitality, 2) == 0.80, ctx.vitality
    assert ctx.speed == 266, ctx.speed
    assert ctx.stamina == 228, ctx.stamina
    assert ctx.power == 196, ctx.power
    assert ctx.guts == 200, ctx.guts
    assert ctx.wisdom == 176, ctx.wisdom
    assert ctx.mood == ctx.MOOD_BAD, ctx.mood


def test_update_by_command_scene_issue12_2():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "command_scene_issue12_2.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 10, 1), ctx.date
    assert round(ctx.vitality, 2) == 0.79, ctx.vitality
    assert ctx.speed == 241, ctx.speed
    assert ctx.stamina == 237, ctx.stamina
    assert ctx.power == 144, ctx.power
    assert ctx.guts == 187, ctx.guts
    assert ctx.wisdom == 184, ctx.wisdom
    assert ctx.mood == ctx.MOOD_GOOD, ctx.mood


def test_update_by_command_scene_issue17():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "command_scene_issue17.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 0, 0), ctx.date
    assert round(ctx.vitality, 2) == 0.53, ctx.vitality
    assert ctx.speed == 195, ctx.speed
    assert ctx.stamina == 150, ctx.stamina
    assert ctx.power == 119, ctx.power
    assert ctx.guts == 115, ctx.guts
    assert ctx.wisdom == 91, ctx.wisdom
    assert ctx.mood == ctx.MOOD_GOOD, ctx.mood


def test_update_by_command_scene_issue17_2():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "command_scene_issue17_2.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 11, 2), ctx.date
    assert round(ctx.vitality, 2) == 1, ctx.vitality
    assert ctx.speed == 262, ctx.speed
    assert ctx.stamina == 266, ctx.stamina
    assert ctx.power == 142, ctx.power
    assert ctx.guts == 156, ctx.guts
    assert ctx.wisdom == 233, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_issue41():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "command_scene_issue41.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_command_scene(img)
    assert ctx.date == (3, 11, 1), ctx.date
    assert round(ctx.vitality, 2) == 0.84, ctx.vitality
    assert ctx.speed == 1200, ctx.speed
    assert ctx.stamina == 753, ctx.stamina
    assert ctx.power == 616, ctx.power
    assert ctx.guts == 364, ctx.guts
    assert ctx.wisdom == 326, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_issue113():
    ctx = Context.new()
    with _test.screenshot("command_scene_issue113.png") as img:
        ctx.update_by_command_scene(img)

    assert ctx.date == (4, 0, 0), ctx.date
    assert round(ctx.vitality, 2) == 0.72, ctx.vitality
    assert ctx.speed == 1144, ctx.speed
    assert ctx.stamina == 482, ctx.stamina
    assert ctx.power == 459, ctx.power
    assert ctx.guts == 343, ctx.guts
    assert ctx.wisdom == 437, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_class_detail():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "class_detail.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    assert ctx.fan_count == 1, ctx.fan_count
    assert ctx.is_after_winning == False, ctx.is_after_winning


def test_update_by_class_detail_2():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "class_detail_2.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    assert ctx.fan_count == 1225, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_3():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "class_detail_3.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    assert ctx.fan_count == 11950, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_4():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "class_detail_4.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    assert ctx.fan_count == 148805, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_5():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "class_detail_5.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    assert ctx.fan_count == 127591, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_6():
    img = PIL.Image.open(_TEST_DATA_PATH / "class_detail_6.png").convert("RGB")
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    assert ctx.fan_count == 121794, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_issue35():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "class_detail_issue35.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    assert ctx.fan_count == 1129, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_issue35_2():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "class_detail_issue35_2.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    assert ctx.fan_count == 4119, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_issue86():
    with _test.screenshot("class_detail_issue86.png") as img:
        ctx = Context.new()
        ctx.update_by_class_detail(img)
    assert ctx.fan_count == 88556, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_character_detail():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "character_detail.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_character_detail(img)

    assert ctx.turf == ctx.STATUS_A, ctx.turf
    assert ctx.dart == ctx.STATUS_G, ctx.dart

    assert ctx.sprint == ctx.STATUS_C, ctx.sprint
    assert ctx.mile == ctx.STATUS_B, ctx.mile
    assert ctx.intermediate == ctx.STATUS_A, ctx.intermediate
    assert ctx.long == ctx.STATUS_C, ctx.long

    assert ctx.lead == ctx.STATUS_D, ctx.lead
    assert ctx.head == ctx.STATUS_A, ctx.head
    assert ctx.middle == ctx.STATUS_A, ctx.middle
    assert ctx.last == ctx.STATUS_G, ctx.last


def test_update_by_character_detail_2():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "character_detail_2.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_character_detail(img)

    assert ctx.turf == ctx.STATUS_A, ctx.turf
    assert ctx.dart == ctx.STATUS_E, ctx.dart

    assert ctx.sprint == ctx.STATUS_D, ctx.sprint
    assert ctx.mile == ctx.STATUS_D, ctx.mile
    assert ctx.intermediate == ctx.STATUS_A, ctx.intermediate
    assert ctx.long == ctx.STATUS_A, ctx.long

    assert ctx.lead == ctx.STATUS_A, ctx.lead
    assert ctx.head == ctx.STATUS_A, ctx.head
    assert ctx.middle == ctx.STATUS_B, ctx.middle
    assert ctx.last == ctx.STATUS_B, ctx.last


def test_update_by_character_detail_3():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "character_detail_3.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_character_detail(img)

    assert ctx.turf == ctx.STATUS_S, ctx.turf
    assert ctx.dart == ctx.STATUS_G, ctx.dart

    assert ctx.sprint == ctx.STATUS_C, ctx.sprint
    assert ctx.mile == ctx.STATUS_B, ctx.mile
    assert ctx.intermediate == ctx.STATUS_A, ctx.intermediate
    assert ctx.long == ctx.STATUS_C, ctx.long

    assert ctx.lead == ctx.STATUS_D, ctx.lead
    assert ctx.head == ctx.STATUS_A, ctx.head
    assert ctx.middle == ctx.STATUS_A, ctx.middle
    assert ctx.last == ctx.STATUS_G, ctx.last


def test_update_by_character_detail_4():
    img = (
        PIL.Image.open(_TEST_DATA_PATH / "character_detail_4.png")
        .convert("RGB")
        .resize((540, 960))
    )
    ctx = Context.new()
    ctx.update_by_character_detail(img)

    assert ctx.turf == ctx.STATUS_A, ctx.turf
    assert ctx.dart == ctx.STATUS_G, ctx.dart

    assert ctx.sprint == ctx.STATUS_C, ctx.sprint
    assert ctx.mile == ctx.STATUS_B, ctx.mile
    assert ctx.intermediate == ctx.STATUS_S, ctx.intermediate
    assert ctx.long == ctx.STATUS_C, ctx.long

    assert ctx.lead == ctx.STATUS_D, ctx.lead
    assert ctx.head == ctx.STATUS_A, ctx.head
    assert ctx.middle == ctx.STATUS_A, ctx.middle
    assert ctx.last == ctx.STATUS_G, ctx.last


def test_update_by_character_detail_5():
    img = PIL.Image.open(_TEST_DATA_PATH / "character_detail_5.png").convert("RGB")
    ctx = Context.new()
    ctx.update_by_character_detail(img)

    assert ctx.turf == ctx.STATUS_A, ctx.turf
    assert ctx.dart == ctx.STATUS_G, ctx.dart

    assert ctx.sprint == ctx.STATUS_C, ctx.sprint
    assert ctx.mile == ctx.STATUS_B, ctx.mile
    assert ctx.intermediate == ctx.STATUS_A, ctx.intermediate
    assert ctx.long == ctx.STATUS_A, ctx.long

    assert ctx.lead == ctx.STATUS_A, ctx.lead
    assert ctx.head == ctx.STATUS_D, ctx.head
    assert ctx.middle == ctx.STATUS_F, ctx.middle
    assert ctx.last == ctx.STATUS_G, ctx.last

    assert ctx.conditions == set((ctx.CONDITION_HEADACHE,)), ctx.conditions


def test_update_by_character_detail_6():
    with _test.screenshot("character_detail_6.png") as img:
        ctx = Context.new()
        ctx.update_by_character_detail(img)

    assert ctx.turf == ctx.STATUS_A, ctx.turf
    assert ctx.dart == ctx.STATUS_E, ctx.dart

    assert ctx.sprint == ctx.STATUS_G, ctx.sprint
    assert ctx.mile == ctx.STATUS_E, ctx.mile
    assert ctx.intermediate == ctx.STATUS_A, ctx.intermediate
    assert ctx.long == ctx.STATUS_A, ctx.long

    assert ctx.lead == ctx.STATUS_C, ctx.lead
    assert ctx.head == ctx.STATUS_A, ctx.head
    assert ctx.middle == ctx.STATUS_A, ctx.middle
    assert ctx.last == ctx.STATUS_G, ctx.last

    assert ctx.conditions == set((ctx.CONDITION_OVERWEIGHT,)), ctx.conditions


def test_update_by_character_detail_issue39():
    img = PIL.Image.open(_TEST_DATA_PATH / "character_detail_issue39.png").convert(
        "RGB"
    )
    ctx = Context.new()
    ctx.update_by_character_detail(img)

    assert ctx.turf == ctx.STATUS_A, ctx.turf
    assert ctx.dart == ctx.STATUS_F, ctx.dart

    assert ctx.sprint == ctx.STATUS_F, ctx.sprint
    assert ctx.mile == ctx.STATUS_C, ctx.mile
    assert ctx.intermediate == ctx.STATUS_A, ctx.intermediate
    assert ctx.long == ctx.STATUS_A, ctx.long

    assert ctx.lead == ctx.STATUS_G, ctx.lead
    assert ctx.head == ctx.STATUS_A, ctx.head
    assert ctx.middle == ctx.STATUS_A, ctx.middle
    assert ctx.last == ctx.STATUS_F, ctx.last

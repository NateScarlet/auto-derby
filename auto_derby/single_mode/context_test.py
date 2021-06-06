from .context import Context

from pathlib import Path
import PIL.Image


_TEST_DATA_PATH = Path(__file__).parent / "test_data"


def test_update_by_command_scene():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 12, 2), ctx.date
    assert ctx.vitality == 0.9162011173184358, ctx.vitality
    assert ctx.speed == 281, ctx.speed
    assert ctx.stamina == 217, ctx.stamina
    assert ctx.power == 210, ctx.power
    assert ctx.guts == 187, ctx.guts
    assert ctx.wisdom == 266, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_2():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_2.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (2, 1, 1), ctx.date
    assert ctx.vitality == 0.9162011173184358, ctx.vitality
    assert ctx.speed == 281, ctx.speed
    assert ctx.stamina == 217, ctx.stamina
    assert ctx.power == 210, ctx.power
    assert ctx.guts == 198, ctx.guts
    assert ctx.wisdom == 266, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_3():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_3.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (3, 1, 1), ctx.date
    assert ctx.vitality == 1, ctx.vitality
    assert ctx.speed == 589, ctx.speed
    assert ctx.stamina == 375, ctx.stamina
    assert ctx.power == 461, ctx.power
    assert ctx.guts == 263, ctx.guts
    assert ctx.wisdom == 386, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_command_scene_issue7():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_issue7.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 0, 0)
    assert ctx.vitality == 1
    assert ctx.speed == 158
    assert ctx.stamina == 190
    assert ctx.power == 67
    assert ctx.guts == 95
    assert ctx.wisdom == 90
    assert ctx.mood == ctx.MOOD_NORMAL


def test_update_by_command_scene_issue12():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_issue12.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 12, 2), ctx.date
    assert ctx.vitality == 0.7932960893854748, ctx.vitality
    assert ctx.speed == 266, ctx.speed
    assert ctx.stamina == 228, ctx.stamina
    assert ctx.power == 196, ctx.power
    assert ctx.guts == 200, ctx.guts
    assert ctx.wisdom == 176, ctx.wisdom
    assert ctx.mood == ctx.MOOD_BAD, ctx.mood


def test_update_by_command_scene_issue12_2():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_issue12_2.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 10, 1), ctx.date
    assert ctx.vitality == 0.7877094972067039, ctx.vitality
    assert ctx.speed == 241, ctx.speed
    assert ctx.stamina == 237, ctx.stamina
    assert ctx.power == 144, ctx.power
    assert ctx.guts == 187, ctx.guts
    assert ctx.wisdom == 184, ctx.wisdom
    assert ctx.mood == ctx.MOOD_GOOD, ctx.mood


def test_update_by_command_scene_issue17():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_issue17.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 0, 0), ctx.date
    assert ctx.vitality == 0.5139664804469274, ctx.vitality
    assert ctx.speed == 195, ctx.speed
    assert ctx.stamina == 150, ctx.stamina
    assert ctx.power == 119, ctx.power
    assert ctx.guts == 115, ctx.guts
    assert ctx.wisdom == 91, ctx.wisdom
    assert ctx.mood == ctx.MOOD_GOOD, ctx.mood


def test_update_by_command_scene_issue17_2():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "command_scene_issue17_2.png").convert("RGB")
    ctx = Context()
    ctx.update_by_command_scene(img)
    assert ctx.date == (1, 11, 2), ctx.date
    assert ctx.vitality == 1, ctx.vitality
    assert ctx.speed == 262, ctx.speed
    assert ctx.stamina == 266, ctx.stamina
    assert ctx.power == 142, ctx.power
    assert ctx.guts == 156, ctx.guts
    assert ctx.wisdom == 233, ctx.wisdom
    assert ctx.mood == ctx.MOOD_VERY_GOOD, ctx.mood


def test_update_by_race_result_scene():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "race_result_scene.png").convert("RGB")
    ctx = Context()
    ctx.update_by_race_result_scene(img)
    assert ctx.fan_count == 1179


def test_update_by_race_result_scene_2():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "race_result_scene_2.png").convert("RGB")
    ctx = Context()
    ctx.update_by_race_result_scene(img)
    assert ctx.fan_count == 4073


def test_update_by_race_result_scene_3():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "race_result_scene_3.png").convert("RGB")
    ctx = Context()
    ctx.update_by_race_result_scene(img)
    assert ctx.fan_count == 134344, ctx.fan_count


def test_update_by_character_class_menu():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "character_class_menu.png").convert("RGB")
    ctx = Context()
    ctx.update_by_character_class_menu(img)
    assert ctx.fan_count == 1, ctx.fan_count


def test_update_by_character_class_menu_2():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "character_class_menu_2.png").convert("RGB")
    ctx = Context()
    ctx.update_by_character_class_menu(img)
    assert ctx.fan_count == 1225, ctx.fan_count


def test_update_by_character_class_menu_3():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "character_class_menu_3.png").convert("RGB")
    ctx = Context()
    ctx.update_by_character_class_menu(img)
    assert ctx.fan_count == 11950, ctx.fan_count


def test_update_by_character_class_menu_4():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "character_class_menu_4.png").convert("RGB")
    ctx = Context()
    ctx.update_by_character_class_menu(img)
    assert ctx.fan_count == 148805, ctx.fan_count


def test_update_by_character_status_menu():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "character_status_menu.png").convert("RGB")
    ctx = Context()
    ctx.update_by_character_status_menu(img)

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


def test_update_by_character_status_menu_2():
    img = PIL.Image.open(
        _TEST_DATA_PATH / "character_status_menu_2.png").convert("RGB")
    ctx = Context()
    ctx.update_by_character_status_menu(img)

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

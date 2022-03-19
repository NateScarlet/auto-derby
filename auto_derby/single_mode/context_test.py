from .. import _test
from .context import Context


def test_update_by_class_detail():
    img, _ = _test.use_screenshot("single_mode/class_detail.png")
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    _test.snapshot_match(ctx)
    assert ctx.fan_count == 1, ctx.fan_count
    assert ctx.is_after_winning == False, ctx.is_after_winning


def test_update_by_class_detail_2():
    img, _ = _test.use_screenshot("single_mode/class_detail_2.png")
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    _test.snapshot_match(ctx)
    assert ctx.fan_count == 1225, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_3():
    img, _ = _test.use_screenshot("single_mode/class_detail_3.png")
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    _test.snapshot_match(ctx)
    assert ctx.fan_count == 11950, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_4():
    img, _ = _test.use_screenshot("single_mode/class_detail_4.png")
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    _test.snapshot_match(ctx)
    assert ctx.fan_count == 148805, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_5():
    img, _ = _test.use_screenshot("single_mode/class_detail_5.png")
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    _test.snapshot_match(ctx)
    assert ctx.fan_count == 127591, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_6():
    img, _ = _test.use_screenshot("single_mode/class_detail_6.png")
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    _test.snapshot_match(ctx)
    assert ctx.fan_count == 121794, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_issue35():
    img, _ = _test.use_screenshot("single_mode/class_detail_issue35.png")
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    _test.snapshot_match(ctx)
    assert ctx.fan_count == 1129, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_issue35_2():
    img, _ = _test.use_screenshot("single_mode/class_detail_issue35_2.png")
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    _test.snapshot_match(ctx)
    assert ctx.fan_count == 4119, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_class_detail_issue86():
    img, _ = _test.use_screenshot("single_mode/class_detail_issue86.png")
    ctx = Context.new()
    ctx.update_by_class_detail(img)
    _test.snapshot_match(ctx)
    assert ctx.fan_count == 88556, ctx.fan_count
    assert ctx.is_after_winning == True, ctx.is_after_winning


def test_update_by_character_detail():
    img, _ = _test.use_screenshot("single_mode/character_detail.png")
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
    img, _ = _test.use_screenshot("single_mode/character_detail_2.png")
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
    img, _ = _test.use_screenshot("single_mode/character_detail_3.png")
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
    img, _ = _test.use_screenshot("single_mode/character_detail_4.png")
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
    img, _ = _test.use_screenshot("single_mode/character_detail_5.png")
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
    img, _ = _test.use_screenshot("single_mode/character_detail_6.png")
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
    img, _ = _test.use_screenshot("single_mode/character_detail_issue39.png")
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


def test_date_from_turn_count_v2():
    for i in range(0, 76):
        ctx = Context.new()
        ctx.date = ctx.date_from_turn_count_v2(i)
        assert ctx.turn_count_v2() == i, ctx.date
    _test.snapshot_match(
        tuple(
            f"{i},{Context.date_from_turn_count_v2(i)}"
            for i in range(1, Context().total_turn_count() + 1)
        )
    )

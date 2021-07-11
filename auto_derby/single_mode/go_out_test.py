from .go_out import Option

from . import _test


def test_from_menu():
    with _test.screenshot("go_out_menu.png") as img:
        res = Option.from_menu(img)

    support_card, character = sorted(res, key=lambda x: x.position[1])
    assert support_card.type == Option.TYPE_SUPPORT, support_card.type
    assert support_card.current_event_count == 0, support_card.current_event_count
    assert character.type == Option.TYPE_MAIN, character.type

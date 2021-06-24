from . import mathtools


def test_resize_proxy_issue71():
    rp = mathtools.ResizeProxy(1080)

    res = rp.vector(-50, 466)
    assert res == -116, res


def test_distance():
    assert mathtools.distance((0,), (1,)) == 1
    assert mathtools.distance((0,), (-1,)) == 1
    assert mathtools.distance((0, 0), (1, 1)) == 1.4142135623730951
    assert mathtools.distance((0, 0), (-1, -1)) == 1.4142135623730951
    assert mathtools.distance((0, 0, 0), (1, 1, 1)) == 1.7320508075688772

from . import mathtools


def test_resize_proxy_issue71():
    rp = mathtools.ResizeProxy(1080)

    res = rp.vector(-50, 466)
    assert res == -116, res

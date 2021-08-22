from . import rest
from ... import _test
from .. import Context


def test_default_score():
    ctx = Context.new()
    ctx.vitality = 0
    vit000 = rest.default_score(ctx)
    ctx.vitality = 0.3
    vit030 = rest.default_score(ctx)
    ctx.vitality = 0.8
    vit080 = rest.default_score(ctx)
    ctx.vitality = 1
    vit100 = rest.default_score(ctx)
    assert vit000 == vit030
    assert vit100 == 0
    if _test.SNAPSHOT_UPDATE:
        _test.snapshot_match(
            {
                "vit=0.0": vit000,
                "vit=0.3": vit030,
                "vit=0.8": vit080,
                "vit=1.0": vit100,
            }
        )

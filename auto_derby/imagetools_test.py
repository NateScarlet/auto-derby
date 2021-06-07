import pytest
from . import imagetools


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (0, 0, 1),
        (0, 255, 0),
        ((0, 0, 0), (0, 0, 0), 1),
        ((0, 0, 0), (255, 255, 255), 0),
        ((0, 0, 0), (10, 10, 10), 0.9320764389188676),
        ((0, 0, 0), (10, 0, 0), 0.9607843137254902),
    ],
)
def test_compare_color(a, b, expected):
    assert imagetools.compare_color(a, b) == expected

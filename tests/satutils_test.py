import pytest
from satutils.map import Canvas

def test_canvas():
    canvas = Canvas(49, 8, 123)
    assert canvas.lat == 49
    assert canvas.lon == 8
    assert canvas.center == [49,8]
    assert canvas.radius == 123
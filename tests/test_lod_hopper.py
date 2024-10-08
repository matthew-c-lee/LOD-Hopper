from lod_hopper.lod_hopper import load_line
import pytest

@pytest.mark.parametrize("start, end", [
    (3000, -3000),
    (3000, 6000),
    (-3000, 6000),
    (-3000, -6000),
    (-3000, -6001),
    (-3000, -5999),
    (-3000, -5526),
    (-6912, -5526),
])
def test_load_line(start, end):
    result = load_line(start, end, 10)
    
    assert result[0] == start
    assert result[-1] == end

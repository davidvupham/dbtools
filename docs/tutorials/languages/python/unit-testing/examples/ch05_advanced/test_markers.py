import pytest
import time

@pytest.mark.slow
def test_heavy_computation():
    time.sleep(0.1)
    assert True

@pytest.mark.skip(reason="Obsolete feature")
def test_old_feature():
    assert False

@pytest.mark.xfail(reason="Known bug")
def test_buggy_feature():
    assert 1 / 0 == 0

def test_fast_math():
    assert 1 + 1 == 2

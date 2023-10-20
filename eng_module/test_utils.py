import utils, pytest

def test_str_to_int():
    test_value1 = utils.str_to_int("43")
    test_value2 = utils.str_to_int("13")
    
    assert test_value1 == pytest.approx(43)
    assert test_value2 == pytest.approx(13)

def test_str_to_float():
    test_value1 = utils.str_to_float("43")
    test_value2 = utils.str_to_float("13.4")
    
    assert test_value1 == pytest.approx(43.0)
    assert test_value2 == pytest.approx(13.4)

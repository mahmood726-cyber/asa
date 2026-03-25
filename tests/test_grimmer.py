"""GRIMMER test: is the reported SD possible given n + mean?"""
import sys
import pytest
sys.path.insert(0, __import__('os').path.dirname(__file__))
from conftest import js

@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    if driver.current_url != app_url:
        driver.get(app_url)

class TestGrimmerBasic:
    def test_pass_simple(self, driver):
        """n=10, mean=3.0, SD=1.0 (1dp): SS=9+90=99, integer -> PASS"""
        r = js(driver, 'grimmerCheck(1.0, 10, 3.0, 1, 1)')
        assert r['pass'] is True

    def test_pass_sd_zero(self, driver):
        """n=5, mean=3.0, SD=0.0: SS=0+45=45, integer -> PASS"""
        r = js(driver, 'grimmerCheck(0.0, 5, 3.0, 1, 1)')
        assert r['pass'] is True

    def test_fail_impossible_sd(self, driver):
        """n=10, mean=3.0, SD=1.23 (2dp): none of the rounding options yield integer SS"""
        r = js(driver, 'grimmerCheck(1.23, 10, 3.0, 1, 2)')
        assert r['pass'] is False

    def test_pass_known_valid(self, driver):
        """n=10, mean=3.0, SD=1.0: Sxi2=99 (integer). Also works at 2dp."""
        r = js(driver, 'grimmerCheck(1.00, 10, 3.0, 1, 2)')
        assert r['pass'] is True

class TestGrimmerEdgeCases:
    def test_n_less_than_2(self, driver):
        """n=1 should SKIP (null pass)"""
        r = js(driver, 'grimmerCheck(1.0, 1, 3.0, 1, 2)')
        assert r['pass'] is None

    def test_negative_sd(self, driver):
        """Negative SD should fail"""
        r = js(driver, 'grimmerCheck(-1.0, 10, 3.0, 1, 2)')
        assert r['pass'] is False

    def test_multi_item(self, driver):
        """n=10, items=3, mean=2.0, SD=0.5 (1dp): scaled by items^2=9"""
        r = js(driver, 'grimmerCheck(0.5, 10, 2.0, 3, 1)')
        assert r['pass'] is not None  # should not be null/skipped

class TestGrimmerConsistency:
    def test_valid_integer_data(self, driver):
        """n=4, mean=2.5, SD=1.29 (2dp):
        Possible dataset: [1, 2, 3, 4] -> mean=2.5, SD=1.2910 -> rounds to 1.29
        Sxi2 = 1+4+9+16 = 30. Check: 1.29^2*3 + 4*6.25 = 4.9923 + 25 = 29.9923 ~30
        With rounding: 1.295^2*3 + 25 = 5.031 + 25 = 30.031 -> rounds to 30 -> PASS"""
        r = js(driver, 'grimmerCheck(1.29, 4, 2.5, 1, 2)')
        assert r['pass'] is True

    def test_another_valid(self, driver):
        """n=5, mean=3.0, SD=1.0 (1dp):
        Possible dataset: [2,2,3,4,4] -> mean=3.0, SD=1.0
        Sxi2=4+4+9+16+16=49. Check: 1.0*4+5*9=4+45=49 -> PASS"""
        r = js(driver, 'grimmerCheck(1.0, 5, 3.0, 1, 1)')
        assert r['pass'] is True

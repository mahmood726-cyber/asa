"""GRIM test: is the reported mean possible given n?"""
import sys
import pytest
sys.path.insert(0, __import__('os').path.dirname(__file__))
from conftest import js

@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    if driver.current_url != app_url:
        driver.get(app_url)

class TestGrimBasic:
    def test_pass_simple(self, driver):
        """n=10, mean=3.1 -> sum=31, integer -> PASS"""
        r = js(driver, 'grimCheck(3.1, 10, 1, 1, "up_or_down")')
        assert r['pass'] is True

    def test_fail_simple(self, driver):
        """n=10, mean=2.45 -> sum=24.5, not integer -> FAIL"""
        r = js(driver, 'grimCheck(2.45, 10, 1, 2, "up_or_down")')
        assert r['pass'] is False

    def test_pass_n20(self, driver):
        """n=20, mean=3.15 -> sum=63, integer -> PASS"""
        r = js(driver, 'grimCheck(3.15, 20, 1, 2, "up_or_down")')
        assert r['pass'] is True

    def test_fail_n25(self, driver):
        """n=25, mean=3.14 -> sum=78.5, not integer -> FAIL"""
        r = js(driver, 'grimCheck(3.14, 25, 1, 2, "up_or_down")')
        assert r['pass'] is False

class TestGrimMultiItem:
    def test_pass_5items(self, driver):
        """n=10, items=5, mean=3.12 -> effectiveN=50, sum=156, integer -> PASS"""
        r = js(driver, 'grimCheck(3.12, 10, 5, 2, "up_or_down")')
        assert r['pass'] is True

    def test_fail_without_items(self, driver):
        """Same mean fails without items param (effectiveN=10, sum=31.2)"""
        r = js(driver, 'grimCheck(3.12, 10, 1, 2, "up_or_down")')
        assert r['pass'] is False

class TestGrimRounding:
    def test_pass_n29_interval(self, driver):
        """n=29, mean=5.9 (1dp): interval [5.85,5.95]*29 = [169.65, 172.55] contains 170,171,172 -> PASS"""
        r = js(driver, 'grimCheck(5.9, 29, 1, 1, "up_or_down")')
        assert r['pass'] is True

    def test_pass_exact_multiple(self, driver):
        """n=20, mean=3.0 -> sum=60, integer -> PASS"""
        r = js(driver, 'grimCheck(3.0, 20, 1, 1, "up_or_down")')
        assert r['pass'] is True

    def test_pass_interval_catches_missed(self, driver):
        """n=17, mean=3.53 (2dp): 3-point check misses but interval [59.925, 60.095] contains 60 -> PASS"""
        r = js(driver, 'grimCheck(3.53, 17, 1, 2, "up_or_down")')
        assert r['pass'] is True

    def test_fail_truly_impossible(self, driver):
        """n=7, mean=3.12 (2dp): interval [3.115, 3.125]*7 = [21.805, 21.875], no integer -> FAIL"""
        r = js(driver, 'grimCheck(3.12, 7, 1, 2, "up_or_down")')
        assert r['pass'] is False

class TestGrimEdgeCases:
    def test_n2(self, driver):
        """n=2, mean=3.5 -> sum=7, integer -> PASS"""
        r = js(driver, 'grimCheck(3.5, 2, 1, 1, "up_or_down")')
        assert r['pass'] is True

    def test_zero_mean(self, driver):
        """n=10, mean=0.0 -> sum=0, integer -> PASS"""
        r = js(driver, 'grimCheck(0.0, 10, 1, 1, "up_or_down")')
        assert r['pass'] is True

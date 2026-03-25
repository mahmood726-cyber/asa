"""SPRITE test: can any dataset of size n produce both the reported mean and SD?"""
import sys
import pytest
sys.path.insert(0, __import__('os').path.dirname(__file__))
from conftest import js

@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    if driver.current_url != app_url:
        driver.get(app_url)

class TestSpriteBasic:
    def test_pass_likert(self, driver):
        """n=10, mean=3.5, SD=1.08, scale 1-5: possible"""
        r = js(driver, 'spriteCheck(3.5, 1.08, 10, 1, 5, 1, 2, 10000)')
        assert r['pass'] is True

    def test_fail_impossible_sd(self, driver):
        """n=10, mean=3.5, SD=0.01, scale 1-5: SD too small for this mean"""
        r = js(driver, 'spriteCheck(3.5, 0.01, 10, 1, 5, 1, 2, 10000)')
        assert r['pass'] is False

    def test_fail_sd_exceeds_range(self, driver):
        """n=10, mean=3.0, SD=5.0, scale 1-5: SD exceeds theoretical max"""
        r = js(driver, 'spriteCheck(3.0, 5.0, 10, 1, 5, 1, 1, 10000)')
        assert r['pass'] is False

    def test_pass_binary(self, driver):
        """n=20, mean=0.6, SD=0.50, scale 0-1 (binary)"""
        r = js(driver, 'spriteCheck(0.6, 0.50, 20, 0, 1, 1, 2, 10000)')
        assert r['pass'] is True

class TestSpriteEdgeCases:
    def test_all_same(self, driver):
        """n=10, mean=3.0, SD=0.0, scale 1-5 -> all values are 3 -> PASS"""
        r = js(driver, 'spriteCheck(3.0, 0.0, 10, 1, 5, 1, 1, 10000)')
        assert r['pass'] is True

    def test_n2(self, driver):
        """n=2 with valid combination"""
        r = js(driver, 'spriteCheck(3.0, 1.41, 2, 1, 5, 1, 2, 10000)')
        assert r['pass'] is True

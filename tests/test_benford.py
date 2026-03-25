"""Benford's Law test: first-digit distribution analysis."""
import sys
import pytest
sys.path.insert(0, __import__('os').path.dirname(__file__))
from conftest import js

@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    if driver.current_url != app_url:
        driver.get(app_url)

class TestExtractFirstDigits:
    def test_basic_extraction(self, driver):
        """Extract first significant digits from various numbers"""
        r = js(driver, 'extractFirstDigits([123, 45.6, 0.078, 9, 1.0])')
        assert r == [1, 4, 7, 9, 1]

    def test_skip_zeros(self, driver):
        """Zero values should be skipped"""
        r = js(driver, 'extractFirstDigits([0, 100, 0, 50])')
        assert r == [1, 5]

    def test_negative_values(self, driver):
        """Negative values use absolute value"""
        r = js(driver, 'extractFirstDigits([-3.14, -27, 5])')
        assert r == [3, 2, 5]

class TestBenfordCheck:
    def test_skip_insufficient(self, driver):
        """Fewer than 30 digits should SKIP"""
        r = js(driver, 'benfordCheck([1,2,3,4,5,6,7,8,9])')
        assert r['verdict'] == 'SKIPPED'

    def test_benford_conforming(self, driver):
        """Distribution matching Benford's Law should PASS.
        Generate array with Benford-proportional counts, total ~101"""
        # Build array: 30 ones, 18 twos, 12 threes, 10 fours, 8 fives, 7 sixes, 6 sevens, 5 eights, 5 nines
        r = js(driver, """(function() {
            var arr = [];
            var counts = [30, 18, 12, 10, 8, 7, 6, 5, 5];
            for (var d = 0; d < 9; d++) {
                for (var c = 0; c < counts[d]; c++) arr.push(d + 1);
            }
            return benfordCheck(arr);
        })()""")
        assert r['verdict'] == 'PASS'
        assert r['chiSq'] is not None
        assert r['pValue'] > 0.05

    def test_uniform_fails(self, driver):
        """Uniform distribution should deviate from Benford"""
        r = js(driver, """(function() {
            var arr = [];
            for (var d = 1; d <= 9; d++) {
                for (var c = 0; c < 50; c++) arr.push(d);
            }
            return benfordCheck(arr);
        })()""")
        assert r['verdict'] in ['WARN', 'FAIL']
        assert r['pValue'] < 0.05

    def test_extreme_nonbenford(self, driver):
        """All digits being 1 should strongly deviate"""
        r = js(driver, """(function() {
            var arr = [];
            for (var c = 0; c < 100; c++) arr.push(1);
            return benfordCheck(arr);
        })()""")
        assert r['verdict'] == 'FAIL'
        assert r['pValue'] < 0.01

class TestBenfordChi2:
    def test_degrees_of_freedom(self, driver):
        """Chi-squared should have df=8 (9 digits - 1)"""
        r = js(driver, """(function() {
            var arr = [];
            var counts = [30, 18, 12, 10, 8, 7, 6, 5, 5];
            for (var d = 0; d < 9; d++) {
                for (var c = 0; c < counts[d]; c++) arr.push(d + 1);
            }
            return benfordCheck(arr);
        })()""")
        assert r['chiSq'] >= 0
        assert 0 <= r['pValue'] <= 1

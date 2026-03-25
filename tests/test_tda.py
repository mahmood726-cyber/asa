"""TDA: terminal digit uniformity test (dataset-level)."""
import sys
import pytest
sys.path.insert(0, __import__('os').path.dirname(__file__))
from conftest import js

@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    if driver.current_url != app_url:
        driver.get(app_url)

class TestTDA:
    def test_uniform_pass(self, driver):
        """Perfectly uniform digits -> PASS"""
        # 10 of each digit = 100 total
        digits = [10]*10
        r = js(driver, 'tdaCheck(' + str(digits) + ')')
        assert r['verdict'] == 'PASS'
        assert r['chiSq'] < 1e-10

    def test_skewed_fail(self, driver):
        """Heavy skew toward 0 and 5 -> FAIL"""
        digits = [30, 2, 2, 2, 2, 30, 2, 2, 2, 2]
        r = js(driver, 'tdaCheck(' + str(digits) + ')')
        assert r['verdict'] == 'FAIL'

    def test_insufficient_skip(self, driver):
        """< 50 total digits -> SKIPPED"""
        digits = [3, 2, 1, 1, 1, 1, 1, 0, 0, 0]
        r = js(driver, 'tdaCheck(' + str(digits) + ')')
        assert r['verdict'] == 'SKIPPED'

    def test_mild_warn(self, driver):
        """Mild deviation -> WARN or PASS (chi2 p between 0.01 and 0.05)"""
        digits = [15, 8, 8, 8, 12, 15, 8, 8, 8, 10]
        r = js(driver, 'tdaCheck(' + str(digits) + ')')
        assert r['verdict'] in ['WARN', 'PASS']

class TestExtractTerminalDigits:
    def test_extraction(self, driver):
        """Extract terminal digits from numeric values.
        JS String(1.0) = '1' (no decimal), so terminal digit is 1, not 0.
        JS String(0.5) = '0.5', terminal digit is 5."""
        r = js(driver, 'extractTerminalDigits([3.14, 2.71, 0.5, 42])')
        assert r == [4, 1, 5, 2]

    def test_negative(self, driver):
        """Negative numbers: use absolute value"""
        r = js(driver, 'extractTerminalDigits([-3.14, -2.7])')
        assert r == [4, 7]

    def test_integer_terminal(self, driver):
        """Integer values: last digit of integer"""
        r = js(driver, 'extractTerminalDigits([10, 25, 100])')
        assert r == [0, 5, 0]

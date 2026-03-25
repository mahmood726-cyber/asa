"""statcheck: recompute p-values from reported test statistics."""
import sys
import pytest
sys.path.insert(0, __import__('os').path.dirname(__file__))
from conftest import js

@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    if driver.current_url != app_url:
        driver.get(app_url)

class TestStatcheckTTest:
    def test_correct_two_tailed(self, driver):
        """t(48)=2.01, reported p=0.05 -> recomputed ~0.05 -> PASS"""
        r = js(driver, 'statcheckVerify("t", 2.01, 48, null, 0.05, 2)')
        assert r['match'] is True

    def test_mismatch(self, driver):
        """t(48)=2.01, reported p=0.001 -> recomputed ~0.05 -> FAIL"""
        r = js(driver, 'statcheckVerify("t", 2.01, 48, null, 0.001, 2)')
        assert r['match'] is False

    def test_decision_error(self, driver):
        """t(30)=2.05, reported p=0.06 -> recomputed ~0.049 -> crosses 0.05 threshold"""
        r = js(driver, 'statcheckVerify("t", 2.05, 30, null, 0.06, 2)')
        assert r['decisionError'] is True

    def test_one_tailed(self, driver):
        """t(20)=1.725, one-tailed p~0.05 -> PASS"""
        r = js(driver, 'statcheckVerify("t", 1.725, 20, null, 0.05, 1)')
        assert r['match'] is True

class TestStatcheckFTest:
    def test_correct_f(self, driver):
        """F(1,48)=4.04, p~0.05 -> PASS"""
        r = js(driver, 'statcheckVerify("F", 4.04, 1, 48, 0.05, 2)')
        assert r['match'] is True

class TestStatcheckChi2:
    def test_correct_chi2(self, driver):
        """chi2(1)=3.84, p~0.05 -> PASS"""
        r = js(driver, 'statcheckVerify("chi2", 3.84, 1, null, 0.05, 2)')
        assert r['match'] is True

class TestStatcheckZ:
    def test_correct_z(self, driver):
        """z=1.96, two-tailed p~0.05 -> PASS"""
        r = js(driver, 'statcheckVerify("z", 1.96, null, null, 0.05, 2)')
        assert r['match'] is True

class TestStatcheckInequality:
    def test_inequality_correct(self, driver):
        """t(48)=3.0, reported "< 0.01" -> recomputed ~0.004 < 0.01 -> PASS"""
        r = js(driver, 'statcheckVerify("t", 3.0, 48, null, "< 0.01", 2)')
        assert r['match'] is True

    def test_inequality_wrong(self, driver):
        """t(48)=1.5, reported "< 0.05" -> recomputed ~0.14 >= 0.05 -> FAIL"""
        r = js(driver, 'statcheckVerify("t", 1.5, 48, null, "< 0.05", 2)')
        assert r['match'] is False

"""Test statistical distribution functions against known R values."""
import sys
import pytest
sys.path.insert(0, __import__('os').path.dirname(__file__))
from conftest import js

@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    if driver.current_url != app_url:
        driver.get(app_url)

class TestNormalCDF:
    def test_pnorm_zero(self, driver):
        assert abs(js(driver, 'pnorm(0)') - 0.5) < 1e-10

    def test_pnorm_196(self, driver):
        assert abs(js(driver, 'pnorm(1.96)') - 0.9750021) < 1e-5

    def test_pnorm_negative(self, driver):
        assert abs(js(driver, 'pnorm(-1.96)') - 0.0249979) < 1e-5

class TestTCDF:
    def test_pt_basic(self, driver):
        # R: pt(2, 10) = 0.9633062
        assert abs(js(driver, 'pt(2, 10)') - 0.9633062) < 1e-5

    def test_pt_negative(self, driver):
        # R: pt(-2, 10) = 0.03669378
        assert abs(js(driver, 'pt(-2, 10)') - 0.03669378) < 1e-5

    def test_pt_large_df(self, driver):
        # R: pt(1.96, 1000) ~= pnorm(1.96)
        assert abs(js(driver, 'pt(1.96, 1000)') - 0.9750021) < 1e-3

class TestChiSqCDF:
    def test_pchisq_basic(self, driver):
        # R: pchisq(3.84, 1) = 0.9500...
        assert abs(js(driver, 'pchisq(3.84, 1)') - 0.9500) < 1e-3

    def test_pchisq_9df(self, driver):
        # R: pchisq(16.92, 9) = 0.9500...
        assert abs(js(driver, 'pchisq(16.92, 9)') - 0.9500) < 1e-3

class TestFCDF:
    def test_pf_basic(self, driver):
        # R: pf(4.0, 1, 10) = 0.9265...
        r = js(driver, 'pf(4.0, 1, 10)')
        assert abs(r - 0.9265) < 1e-3

class TestGammainc:
    def test_gammainc_basic(self, driver):
        # gammainc(1, 1) = 1 - exp(-1) ~= 0.6321
        assert abs(js(driver, 'gammainc(1, 1)') - 0.6321) < 1e-3

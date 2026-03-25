"""Cross-study duplication detection test."""
import sys
import pytest
sys.path.insert(0, __import__('os').path.dirname(__file__))
from conftest import js

@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    if driver.current_url != app_url:
        driver.get(app_url)

class TestDuplicationBasic:
    def test_no_duplication(self, driver):
        """Two distinct studies should PASS"""
        r = js(driver, """duplicationCheck([
            {study:'A', n_t:10, n_c:12, mean_t:3.1, mean_c:2.9, sd_t:1.0, sd_c:1.1},
            {study:'B', n_t:20, n_c:22, mean_t:4.5, mean_c:4.0, sd_t:1.5, sd_c:1.3}
        ])""")
        assert r['verdict'] == 'PASS'
        assert len(r['flaggedPairs']) == 0

    def test_identical_studies_flagged(self, driver):
        """Two identical studies should be flagged"""
        r = js(driver, """duplicationCheck([
            {study:'A', n_t:10, n_c:12, mean_t:3.1, mean_c:2.9, sd_t:1.0, sd_c:1.1},
            {study:'B', n_t:10, n_c:12, mean_t:3.1, mean_c:2.9, sd_t:1.0, sd_c:1.1}
        ])""")
        assert r['verdict'] == 'FAIL'
        assert len(r['flaggedPairs']) == 1
        assert r['flaggedPairs'][0]['matches'] == 6

    def test_partial_match_not_flagged(self, driver):
        """Studies sharing only 2 fields should not be flagged (threshold=4)"""
        r = js(driver, """duplicationCheck([
            {study:'A', n_t:10, n_c:12, mean_t:3.1, mean_c:2.9, sd_t:1.0, sd_c:1.1},
            {study:'B', n_t:10, n_c:12, mean_t:5.0, mean_c:4.0, sd_t:2.0, sd_c:2.5}
        ])""")
        assert r['verdict'] == 'PASS'

class TestDuplicationEdgeCases:
    def test_single_study_skips(self, driver):
        """Single study should SKIP"""
        r = js(driver, """duplicationCheck([
            {study:'A', n_t:10, n_c:12, mean_t:3.1, mean_c:2.9, sd_t:1.0, sd_c:1.1}
        ])""")
        assert r['verdict'] == 'SKIPPED'

    def test_empty_array_skips(self, driver):
        """Empty array should SKIP"""
        r = js(driver, 'duplicationCheck([])')
        assert r['verdict'] == 'SKIPPED'

    def test_multiple_pairs_flagged(self, driver):
        """Three identical studies should flag 3 pairs"""
        r = js(driver, """duplicationCheck([
            {study:'A', n_t:10, n_c:12, mean_t:3.1, mean_c:2.9, sd_t:1.0, sd_c:1.1},
            {study:'B', n_t:10, n_c:12, mean_t:3.1, mean_c:2.9, sd_t:1.0, sd_c:1.1},
            {study:'C', n_t:10, n_c:12, mean_t:3.1, mean_c:2.9, sd_t:1.0, sd_c:1.1}
        ])""")
        assert r['verdict'] == 'FAIL'
        assert len(r['flaggedPairs']) == 3  # A-B, A-C, B-C

    def test_studies_without_numeric_data(self, driver):
        """Studies with only statcheck data (no n/mean/sd) should skip"""
        r = js(driver, """duplicationCheck([
            {study:'A', test_stat:2.0, stat_type:'t', df:30, p_reported:'0.05'},
            {study:'B', test_stat:1.5, stat_type:'t', df:20, p_reported:'0.10'}
        ])""")
        assert r['verdict'] == 'SKIPPED'

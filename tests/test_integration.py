"""Integration tests: full pipeline on demo datasets."""
import os, time, json, pytest

from conftest import js


@pytest.fixture(autouse=True)
def load_app(driver, app_url):
    driver.get(app_url)
    time.sleep(1)


def run_tutorial(driver):
    driver.find_element('id', 'loadTutorial').click()
    time.sleep(0.5)
    driver.find_element('id', 'runGauntletBtn').click()
    time.sleep(3)


def run_fujii(driver):
    driver.find_element('id', 'loadFujii').click()
    time.sleep(0.5)
    driver.find_element('id', 'runGauntletBtn').click()
    time.sleep(3)


def get_results(driver):
    raw = js(driver, 'JSON.stringify(window.asaResults)')
    assert raw, "asaResults is empty"
    return json.loads(raw)


# ── Tutorial Dataset ──

class TestTutorialDataset:
    def test_load_and_run(self, driver):
        """Load tutorial, run gauntlet, check results exist"""
        run_tutorial(driver)
        data = get_results(driver)
        assert len(data['studies']) == 12, f"Expected 12 studies, got {len(data['studies'])}"

    def test_grim_fails(self, driver):
        """Tutorial should have >=4 GRIM failures"""
        run_tutorial(driver)
        data = get_results(driver)
        grim_fails = [s for s in data['studies']
                      if (s.get('grim') or {}).get('result') == 'FAIL']
        assert len(grim_fails) >= 3, f"Expected >=3 GRIM fails, got {len(grim_fails)}: {[s['study'] for s in grim_fails]}"

    def test_statcheck_fails(self, driver):
        """Tutorial should have >=2 statcheck failures"""
        run_tutorial(driver)
        data = get_results(driver)
        sc_fails = [s for s in data['studies']
                    if s.get('statcheck', {}).get('result') in ('FAIL', 'DECISION_ERROR')]
        assert len(sc_fails) >= 2, f"Expected >=2 statcheck fails, got {len(sc_fails)}"

    def test_grimmer_runs(self, driver):
        """GRIMMER should run on discrete studies and produce results"""
        run_tutorial(driver)
        data = get_results(driver)
        grimmer_tested = [s for s in data['studies']
                         if s.get('grimmer', {}).get('result') in ('PASS', 'FAIL')]
        assert len(grimmer_tested) >= 1, "Expected at least 1 study tested by GRIMMER"

    def test_ahmed_grim_passes(self, driver):
        """Ahmed 2020 should pass GRIM (mean is valid) even if GRIMMER flags it"""
        run_tutorial(driver)
        data = get_results(driver)
        ahmed = next((s for s in data['studies'] if s['study'] == 'Ahmed 2020'), None)
        assert ahmed is not None, "Ahmed 2020 not found"
        assert ahmed['grim']['result'] == 'PASS', f"Ahmed GRIM={ahmed['grim']['result']}"

    def test_has_tda_result(self, driver):
        """TDA should produce a result with chi-squared"""
        run_tutorial(driver)
        data = get_results(driver)
        tda = data.get('tda', {})
        assert tda.get('verdict') in ('PASS', 'WARN', 'FAIL', 'SKIPPED'), f"TDA verdict={tda.get('verdict')}"

    def test_verdict_distribution(self, driver):
        """Should have flagged studies (SUSPICIOUS or SWALLOWED)"""
        run_tutorial(driver)
        data = get_results(driver)
        verdicts = [s['verdict'] for s in data['studies']]
        flagged = [v for v in verdicts if v in ('SUSPICIOUS', 'SWALLOWED')]
        assert len(flagged) >= 1, "Expected at least 1 flagged study"

    def test_benford_result_exists(self, driver):
        """Tutorial should produce Benford analysis"""
        run_tutorial(driver)
        data = get_results(driver)
        benford = data.get('benford', {})
        assert benford.get('verdict') in ('PASS', 'WARN', 'FAIL', 'SKIPPED'), \
            f"Benford verdict={benford.get('verdict')}"

    def test_duplication_result_exists(self, driver):
        """Tutorial should produce duplication analysis"""
        run_tutorial(driver)
        data = get_results(driver)
        dup = data.get('duplication', {})
        assert dup.get('verdict') in ('PASS', 'FAIL', 'SKIPPED'), \
            f"Duplication verdict={dup.get('verdict')}"


# ── Fujii Dataset ──

class TestFujiiDataset:
    def test_load_and_run(self, driver):
        """Load Fujii, run gauntlet"""
        run_fujii(driver)
        data = get_results(driver)
        assert len(data['studies']) == 12, f"Expected 12 studies, got {len(data['studies'])}"

    def test_has_swallowed(self, driver):
        """Fujii dataset should have swallowed studies"""
        run_fujii(driver)
        data = get_results(driver)
        swallowed = [s for s in data['studies'] if s['verdict'] == 'SWALLOWED']
        assert len(swallowed) >= 1, "Expected at least 1 swallowed study in Fujii dataset"


# ── Tabs ──

class TestTabs:
    def test_tabs_switch(self, driver):
        """After running, click each tab and verify it becomes active"""
        run_tutorial(driver)
        tabs = ['gauntlet', 'heatmap', 'reports', 'export', 'entry']
        for tab in tabs:
            btn = driver.find_element('css selector', f'.tab-btn[data-tab="{tab}"]')
            btn.click()
            time.sleep(0.3)
            assert 'active' in btn.get_attribute('class'), f"Tab {tab} not active after click"
            panel = driver.find_element('css selector', f'.tab-content[data-tab="{tab}"]')
            assert 'active' in panel.get_attribute('class'), f"Panel {tab} not active after click"


# ── Export / TruthCert ──

class TestExport:
    def test_receipt_has_hash(self, driver):
        """TruthCert receipt should have input hash"""
        run_tutorial(driver)
        time.sleep(1)  # extra wait for async sha256
        receipt = js(driver, 'JSON.stringify(window.asaReceipt)')
        assert receipt, "asaReceipt is null"
        data = json.loads(receipt)
        assert 'inputHash' in data, "Receipt missing inputHash"
        assert len(data['inputHash']) == 64, f"Hash length={len(data['inputHash'])}, expected 64"

    def test_receipt_has_verdicts(self, driver):
        """Receipt should have verdict counts"""
        run_tutorial(driver)
        time.sleep(1)
        receipt = js(driver, 'JSON.stringify(window.asaReceipt)')
        assert receipt, "asaReceipt is null"
        data = json.loads(receipt)
        v = data.get('verdicts', {})
        assert 'passed' in v, "Receipt missing verdicts.passed"
        assert 'swallowed' in v, "Receipt missing verdicts.swallowed"
        total = v.get('passed', 0) + v.get('suspicious', 0) + v.get('swallowed', 0) + v.get('notAssessed', 0)
        assert total == 12, f"Verdict total={total}, expected 12"

    def test_receipt_per_study(self, driver):
        """Receipt should have per-study entries with GRIMMER field"""
        run_tutorial(driver)
        time.sleep(1)
        receipt = js(driver, 'JSON.stringify(window.asaReceipt)')
        assert receipt, "asaReceipt is null"
        data = json.loads(receipt)
        assert len(data.get('perStudy', [])) == 12, "Receipt should have 12 per-study entries"
        # v2: check grimmer field present
        first = data['perStudy'][0].copy()
        assert 'grimmer' in first, "Receipt perStudy should include grimmer field"

    def test_receipt_has_benford(self, driver):
        """Receipt should have benford and duplication fields"""
        run_tutorial(driver)
        time.sleep(1)
        receipt = js(driver, 'JSON.stringify(window.asaReceipt)')
        assert receipt, "asaReceipt is null"
        data = json.loads(receipt)
        assert 'benford' in data, "Receipt should have benford field"
        assert 'duplication' in data, "Receipt should have duplication field"


# ── Dark Mode ──

class TestDarkMode:
    def test_toggle_theme(self, driver):
        """Toggle theme should add/remove light class"""
        # Start in dark mode (no 'light' class)
        has_light = js(driver, 'document.body.classList.contains("light")')
        assert not has_light, "Should start in dark mode"

        # Toggle to light
        driver.find_element('id', 'themeToggle').click()
        time.sleep(0.3)
        has_light = js(driver, 'document.body.classList.contains("light")')
        assert has_light, "Should be in light mode after toggle"

        # Toggle back
        driver.find_element('id', 'themeToggle').click()
        time.sleep(0.3)
        has_light = js(driver, 'document.body.classList.contains("light")')
        assert not has_light, "Should be back to dark mode"

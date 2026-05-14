import pytest, os, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if not os.environ.get("RUN_BROWSER_TESTS"):
    collect_ignore_glob = [
        "test_benford.py",
        "test_duplication.py",
        "test_grim.py",
        "test_grimmer.py",
        "test_integration.py",
        "test_math.py",
        "test_sprite.py",
        "test_statcheck.py",
        "test_tda.py",
    ]
else:
    collect_ignore_glob = []

@pytest.fixture(scope='session')
def driver():
    opts = Options()
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-gpu')
    opts.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    d = webdriver.Chrome(options=opts)
    d.set_page_load_timeout(30)
    yield d
    d.quit()

@pytest.fixture(scope='session')
def app_url():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'asa.html'))
    return 'file:///' + path.replace('\\', '/')

def js(driver, script):
    """Execute JS and return result."""
    return driver.execute_script('return ' + script)

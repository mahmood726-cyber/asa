import pytest, os, sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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

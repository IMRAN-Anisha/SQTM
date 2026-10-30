"""
conftest.py
pytest fixtures shared by all of Anisha Imran's test files.
pytest loads this file automatically before running the tests.
"""

import os

import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from helpers import save_screenshot

# How long (seconds) explicit waits keep trying before giving up.
# Kept generous because the demo site can be slow on a mobile hotspot.
WAIT_SECONDS = int(os.getenv("WAIT_SECONDS", "20"))


@pytest.fixture
def driver():
    """Start a fresh Chrome window for each scenario and close it afterwards."""
    options = webdriver.ChromeOptions()
    # The demo site's HTTPS certificate triggers warnings; accept it in the test browser only
    options.accept_insecure_certs = True
    options.add_argument("--window-size=1400,1000")
    # Optional: run without a visible window by setting HEADLESS=1
    if os.getenv("HEADLESS") == "1":
        options.add_argument("--headless=new")
    # Selenium Manager downloads the matching ChromeDriver automatically
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


@pytest.fixture
def wait(driver):
    """Explicit wait object: waits for a condition instead of sleeping a fixed time."""
    return WebDriverWait(driver, WAIT_SECONDS)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """If a scenario fails, capture a screenshot automatically as evidence."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            save_screenshot(drv, f"FAILED_{item.name}")

"""
helpers.py
Shared helper functions for Anisha Imran's product discovery tests
(F4 Product Search, F5 Product Filtering / Sorting, F6 Product Details).

Website under test: OpenCart demo store - https://opencart.abstracta.us/
"""

import re
from pathlib import Path
from urllib.parse import urlencode

from selenium.webdriver.common.by import By

# Base address of every page on the store (OpenCart routes pages with ?route=...)
BASE_URL = "https://opencart.abstracta.us/index.php"

# Folder where screenshot evidence for the report is saved
SCREENSHOT_DIR = Path("results/screenshots")

# Text OpenCart shows when a search/filter returns nothing
NO_RESULTS_TEXT = "There is no product that matches the search criteria."

# CSS selectors used across the tests (found with Chrome DevTools > Inspect)
PRODUCT_CARD = ".product-layout .product-thumb"      # one product tile in a listing
PRODUCT_NAME_LINK = ".product-thumb .caption h4 a"   # product name link inside a tile
PRODUCT_PRICE = ".product-thumb .price"              # price block inside a tile


def page_url(route, **params):
    """Build a store URL, e.g. page_url('product/category', path=20)."""
    query = {"route": route, **params}
    return f"{BASE_URL}?{urlencode(query)}"


def save_screenshot(driver, name):
    """Save a full-window screenshot as evidence, e.g. results/screenshots/T004_S1.png."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOT_DIR / f"{name}.png"
    driver.save_screenshot(str(path))
    print(f"    screenshot saved -> {path}")
    return path


def check(condition, message):
    """Print a readable PASS/FAIL line for the terminal evidence, then assert it."""
    print(f"    [{'PASS' if condition else 'FAIL'}] {message}")
    assert condition, message


def product_names(driver):
    """Return the names of all product tiles currently shown in a listing."""
    return [a.text.strip() for a in driver.find_elements(By.CSS_SELECTOR, PRODUCT_NAME_LINK)]


def _money_to_float(text):
    """Turn '$1,202.00' into 1202.0."""
    return float(text.replace(",", ""))


def listing_sort_price(price_element):
    """
    Return the number OpenCart sorts by for one listing tile.

    A tile's price block can look like either of these:
        "$122.00 Ex Tax: $100.00"                  (normal price)
        "$110.00 $122.00 Ex Tax: $90.00"           (special offer: new, old, ex-tax)
    OpenCart sorts on the ex-tax price (using the special price when there is one),
    so the 'Ex Tax' figure is the fairest value to compare. If tax display is
    switched off, fall back to the special price or the first price shown.
    """
    text = price_element.text
    ex_tax = re.search(r"Ex Tax:\s*\D?([\d,]+\.\d{2})", text)
    if ex_tax:
        return _money_to_float(ex_tax.group(1))
    specials = price_element.find_elements(By.CSS_SELECTOR, ".price-new")
    source = specials[0].text if specials else text
    first = re.search(r"([\d,]+\.\d{2})", source)
    return _money_to_float(first.group(1))


def listing_display_price(price_element):
    """
    Return the price a shopper sees first on a listing tile, as text (e.g. '$110.00').
    For a special offer this is the new (discounted) price, otherwise the normal price.
    """
    specials = price_element.find_elements(By.CSS_SELECTOR, ".price-new")
    if specials:
        return specials[0].text.strip()
    return price_element.text.strip().splitlines()[0].split(" ")[0]

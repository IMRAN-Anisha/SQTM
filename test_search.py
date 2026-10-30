"""
T004 - F4 Product Search
Tester: Anisha Imran

Scenario 1: Valid keyword returns matching products        (success case)
Scenario 2: Keyword with no matching product               (failure case)
Scenario 3: Empty search submitted                         (boundary / failure case)

Run:  python -m pytest test_search.py -v -s
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from helpers import (
    NO_RESULTS_TEXT,
    PRODUCT_CARD,
    check,
    page_url,
    product_names,
    save_screenshot,
)

# Header search box and its magnifying-glass button (present on every page)
HEADER_SEARCH_INPUT = (By.CSS_SELECTOR, "#search input[name='search']")
HEADER_SEARCH_BUTTON = (By.CSS_SELECTOR, "#search button")


def search_from_header(driver, wait, keyword):
    """Open the home page, type a keyword into the header search bar and submit it."""
    driver.get(page_url("common/home"))
    box = wait.until(EC.visibility_of_element_located(HEADER_SEARCH_INPUT))
    box.clear()
    if keyword:
        box.send_keys(keyword)
    driver.find_element(*HEADER_SEARCH_BUTTON).click()
    # Clicking search loads the search results page (route=product/search)
    wait.until(EC.url_contains("route=product/search"))


def test_T004_S1_valid_keyword_returns_matching_products(driver, wait):
    """A real keyword, typed in lower case, returns only products whose names contain it."""
    print("\nT004-S1 Valid keyword search")
    keyword = "macbook"  # store has MacBook, MacBook Air, MacBook Pro

    search_from_header(driver, wait, keyword)

    # Wait until at least one product tile has been rendered
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_CARD)))
    names = product_names(driver)
    print(f"    results: {names}")

    check(f"search={keyword}" in driver.current_url, "URL carries the search keyword")
    heading = driver.find_element(By.CSS_SELECTOR, "#content h1").text
    check(keyword.lower() in heading.lower(), f"page heading mentions keyword ('{heading}')")
    check(len(names) >= 1, f"at least one product returned ({len(names)} found)")
    # Search is case-insensitive: 'macbook' should match 'MacBook'
    check(all(keyword in n.lower() for n in names), "every result name contains the keyword")

    save_screenshot(driver, "T004_S1_valid_keyword")


def test_T004_S2_unknown_keyword_shows_no_results_message(driver, wait):
    """A keyword that matches nothing shows the 'no product matches' message and no tiles."""
    print("\nT004-S2 Keyword with no matches")
    keyword = "zzqx-not-a-product"

    search_from_header(driver, wait, keyword)

    # Wait for the main content area, then read its text
    content = wait.until(EC.visibility_of_element_located((By.ID, "content")))
    tiles = driver.find_elements(By.CSS_SELECTOR, PRODUCT_CARD)

    check(len(tiles) == 0, "no product tiles are displayed")
    check(NO_RESULTS_TEXT in content.text, f"message shown: '{NO_RESULTS_TEXT}'")

    save_screenshot(driver, "T004_S2_no_results")


def test_T004_S3_empty_search_lists_no_products(driver, wait):
    """Submitting an empty search opens the search page without listing any products or erroring."""
    print("\nT004-S3 Empty search")

    search_from_header(driver, wait, "")

    wait.until(EC.visibility_of_element_located((By.ID, "content")))
    tiles = driver.find_elements(By.CSS_SELECTOR, PRODUCT_CARD)
    # The advanced search form should still be offered so the user can try again
    criteria_box = driver.find_elements(By.ID, "input-search")

    check("search=" not in driver.current_url, "no keyword was sent in the URL")
    check(len(tiles) == 0, "no products are listed for an empty search")
    check(len(criteria_box) == 1 and criteria_box[0].is_displayed(),
          "search criteria form is shown so the user can enter a keyword")
    check("error" not in driver.title.lower(), "page loads without an error page")

    save_screenshot(driver, "T004_S3_empty_search")

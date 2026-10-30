"""
T005 - F5 Product Filtering / Sorting
Tester: Anisha Imran

Scenario 1: Sort a category by Price (Low > High)                  (success case)
Scenario 2: Sort a category by Name (Z - A)                        (success case)
Scenario 3: Filter a search by a category that has no match        (failure case)

Run:  python -m pytest test_filter_sort.py -v -s
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from helpers import (
    NO_RESULTS_TEXT,
    PRODUCT_CARD,
    PRODUCT_PRICE,
    check,
    listing_sort_price,
    page_url,
    product_names,
    save_screenshot,
)

# "Show All Desktops" category (path=20). limit=100 puts every product on one page,
# so the sort order can be checked across the whole category, not just page 1.
DESKTOPS_URL = page_url("product/category", path=20, limit=100)


def open_category(driver, wait):
    """Open the Desktops category and wait for its product tiles."""
    driver.get(DESKTOPS_URL)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_CARD)))


def choose_sort_option(driver, wait, visible_text, expected_url_part):
    """Pick an option from the 'Sort By' dropdown and wait for the re-sorted page."""
    first_tile = driver.find_element(By.CSS_SELECTOR, PRODUCT_CARD)
    Select(driver.find_element(By.ID, "input-sort")).select_by_visible_text(visible_text)
    # Choosing an option reloads the page; wait for the old tiles to disappear...
    wait.until(EC.staleness_of(first_tile))
    # ...then for the URL to carry the new sort and for new tiles to appear
    wait.until(EC.url_contains(expected_url_part))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_CARD)))


def test_T005_S1_sort_by_price_low_to_high(driver, wait):
    """After choosing Price (Low > High), every price is >= the one before it."""
    print("\nT005-S1 Sort by Price (Low > High)")
    open_category(driver, wait)

    choose_sort_option(driver, wait, "Price (Low > High)", "sort=p.price")

    prices = [listing_sort_price(p) for p in driver.find_elements(By.CSS_SELECTOR, PRODUCT_PRICE)]
    print(f"    ex-tax prices in page order: {prices}")

    check("order=ASC" in driver.current_url, "URL shows ascending order")
    check(len(prices) >= 2, f"enough products to compare ({len(prices)})")
    check(prices == sorted(prices), "prices are in ascending order")
    selected = Select(driver.find_element(By.ID, "input-sort")).first_selected_option.text
    check(selected == "Price (Low > High)", f"dropdown keeps the chosen option ('{selected}')")

    save_screenshot(driver, "T005_S1_price_low_high")


def test_T005_S2_sort_by_name_z_to_a(driver, wait):
    """After choosing Name (Z - A), product names are in reverse alphabetical order."""
    print("\nT005-S2 Sort by Name (Z - A)")
    open_category(driver, wait)
    count_before = len(product_names(driver))

    choose_sort_option(driver, wait, "Name (Z - A)", "sort=pd.name")

    names = product_names(driver)
    print(f"    names in page order: {names}")
    # OpenCart compares names case-insensitively, so compare lower-case versions
    lowered = [n.lower() for n in names]

    check("order=DESC" in driver.current_url, "URL shows descending order")
    check(lowered == sorted(lowered, reverse=True), "names are in Z to A order")
    check(len(names) == count_before, "sorting did not add or drop any products")

    save_screenshot(driver, "T005_S2_name_z_a")


def test_T005_S3_category_filter_with_no_match(driver, wait):
    """
    'iphone' finds the iPhone when searching all categories, but filtering the
    same search to the Cameras category must return no products.
    """
    print("\nT005-S3 Category filter excludes non-matching products")

    # Step 1: baseline search across All Categories proves the product exists
    driver.get(page_url("product/search", search="iphone"))
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_CARD)))
    unfiltered = product_names(driver)
    print(f"    all-category results: {unfiltered}")
    check(len(unfiltered) >= 1, "keyword returns products when no category filter is applied")

    # Step 2: apply the category filter from the Search Criteria form
    Select(driver.find_element(By.NAME, "category_id")).select_by_visible_text("Cameras")
    first_tile = driver.find_element(By.CSS_SELECTOR, PRODUCT_CARD)
    driver.find_element(By.ID, "button-search").click()
    wait.until(EC.staleness_of(first_tile))
    wait.until(EC.url_contains("category_id="))

    content = wait.until(EC.visibility_of_element_located((By.ID, "content")))
    filtered = product_names(driver)
    print(f"    Cameras-only results: {filtered}")

    check(len(filtered) == 0, "no products are listed once filtered to Cameras")
    check(NO_RESULTS_TEXT in content.text, f"message shown: '{NO_RESULTS_TEXT}'")
    chosen = Select(driver.find_element(By.NAME, "category_id")).first_selected_option.text
    check(chosen.strip() == "Cameras", "the Cameras filter stays selected after searching")

    save_screenshot(driver, "T005_S3_category_filter_no_match")

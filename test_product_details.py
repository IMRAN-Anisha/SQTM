"""
T006 - F6 Product Details
Tester: Anisha Imran

Scenario 1: Open a product from search results; all key details shown   (success case)
Scenario 2: Name and price on the details page match the listing        (success case)
Scenario 3: Non-existent product ID shows 'Product not found!'           (failure case)

Run:  python -m pytest test_product_details.py -v -s
"""

import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from helpers import (
    PRODUCT_CARD,
    PRODUCT_NAME_LINK,
    PRODUCT_PRICE,
    check,
    listing_display_price,
    page_url,
    save_screenshot,
)

# Elements on a product details page (OpenCart default theme)
DETAIL_NAME = (By.CSS_SELECTOR, "#content h1")
# The selling price is the <h2> inside the right-hand price list
DETAIL_PRICE = (By.XPATH, "//div[@id='content']//ul[contains(@class,'list-unstyled')]//h2")
DETAIL_IMAGE = (By.CSS_SELECTOR, "#content ul.thumbnails img")
DETAIL_AVAILABILITY = (By.XPATH, "//div[@id='content']//li[contains(normalize-space(.),'Availability:')]")
DETAIL_ADD_TO_CART = (By.ID, "button-cart")
DETAIL_QUANTITY = (By.ID, "input-quantity")
DESCRIPTION_TAB = (By.ID, "tab-description")

MONEY = re.compile(r"^\D?[\d,]+\.\d{2}$")  # e.g. $123.20


def test_T006_S1_product_page_shows_key_details(driver, wait):
    """Clicking a search result opens its page with name, price, image, stock, description and cart button."""
    print("\nT006-S1 Product details from search results")

    driver.get(page_url("product/search", search="iphone"))
    link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, PRODUCT_NAME_LINK)))
    clicked_name = link.text.strip()
    print(f"    opening: {clicked_name}")
    link.click()

    name = wait.until(EC.visibility_of_element_located(DETAIL_NAME)).text.strip()
    price = driver.find_element(*DETAIL_PRICE).text.strip()
    availability = driver.find_element(*DETAIL_AVAILABILITY).text.strip()
    images = driver.find_elements(*DETAIL_IMAGE)
    description = driver.find_element(*DESCRIPTION_TAB).text.strip()

    check("route=product/product" in driver.current_url, "a product details page opened")
    check(name == clicked_name, f"heading matches the clicked product ('{name}')")
    check(bool(MONEY.match(price)), f"a price is displayed ('{price}')")
    check(len(images) >= 1 and images[0].is_displayed(), f"product image shown ({len(images)} images)")
    check(availability.startswith("Availability:") and len(availability) > len("Availability:"),
          f"stock status shown ('{availability}')")
    check(len(description) > 0, "description tab contains text")
    check(driver.find_element(*DETAIL_QUANTITY).is_displayed(), "quantity field is shown")
    check(driver.find_element(*DETAIL_ADD_TO_CART).is_enabled(), "Add to Cart button is available")

    save_screenshot(driver, "T006_S1_product_details")


def test_T006_S2_details_match_listing(driver, wait):
    """For the first three Desktops products, the details page shows the same name and price as the listing."""
    print("\nT006-S2 Listing vs details consistency")
    listing_url = page_url("product/category", path=20)

    for index in range(3):
        driver.get(listing_url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_CARD)))
        tile = driver.find_elements(By.CSS_SELECTOR, PRODUCT_CARD)[index]

        # Read what the shopper sees on the listing tile
        list_name = tile.find_element(By.CSS_SELECTOR, ".caption h4 a").text.strip()
        list_price = listing_display_price(tile.find_element(By.CSS_SELECTOR, ".price"))
        print(f"    listing #{index + 1}: {list_name} @ {list_price}")

        tile.find_element(By.CSS_SELECTOR, ".caption h4 a").click()
        detail_name = wait.until(EC.visibility_of_element_located(DETAIL_NAME)).text.strip()
        detail_price = driver.find_element(*DETAIL_PRICE).text.strip()
        print(f"    details    : {detail_name} @ {detail_price}")

        check(detail_name == list_name, f"name matches for '{list_name}'")
        check(detail_price == list_price, f"price matches for '{list_name}' ({list_price})")

        if index == 0:
            save_screenshot(driver, "T006_S2_details_match_listing")


def test_T006_S3_invalid_product_id_shows_not_found(driver, wait):
    """Requesting a product that does not exist shows 'Product not found!' and no purchase controls."""
    print("\nT006-S3 Non-existent product ID")

    driver.get(page_url("product/product", product_id=999999))
    content = wait.until(EC.visibility_of_element_located((By.ID, "content")))
    heading = content.text.strip()
    continue_links = driver.find_elements(By.LINK_TEXT, "Continue")

    check("Product not found!" in heading, f"message reads 'Product not found!' ('{heading}')")
    check(len(continue_links) >= 1, "a Continue button is offered to leave the error page")
    check(len(driver.find_elements(*DETAIL_ADD_TO_CART)) == 0, "no Add to Cart button is offered")
    check(len(driver.find_elements(*DETAIL_PRICE)) == 0, "no price is displayed")

    save_screenshot(driver, "T006_S3_product_not_found")

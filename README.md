# OpenCart product discovery tests (T004–T006)

Tester: Anisha Imran — F4 Product Search, F5 Product Filtering / Sorting, F6 Product Details
Site under test: https://opencart.abstracta.us/

| File | Test case | Scenarios |
|---|---|---|
| `test_search.py` | T004 – F4 Product Search | S1 valid keyword · S2 no-match keyword · S3 empty search |
| `test_filter_sort.py` | T005 – F5 Filtering / Sorting | S1 price low→high · S2 name Z→A · S3 category filter with no match |
| `test_product_details.py` | T006 – F6 Product Details | S1 details shown · S2 listing vs details match · S3 invalid product ID |
| `helpers.py` | shared selectors, URL builder, price parsing, screenshots | |
| `conftest.py` | Chrome driver fixture, explicit waits, screenshot on failure | |

## Setup (macOS / Linux)

```bash
cd opencart-product-tests
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Google Chrome must be installed. Selenium Manager downloads ChromeDriver automatically.

## Run all nine scenarios and save evidence

```bash
mkdir -p results
python -m pytest test_search.py test_filter_sort.py test_product_details.py \
  -v -s --junitxml=results/test_results.xml 2>&1 | tee results/test_results.txt
```

- Each scenario prints `[PASS]` / `[FAIL]` lines for every check — screenshot the terminal for the report.
- Screenshots of each scenario are saved to `results/screenshots/` (failures are saved as `FAILED_<test>.png`).
- If the site is slow (e.g. on a hotspot), raise the wait: `WAIT_SECONDS=40 python -m pytest ...`
- If the university network blocks the site, use a personal hotspot (same issue Kingsley hit).

Run one scenario on its own, e.g.:

```bash
python -m pytest test_search.py::test_T004_S2_unknown_keyword_shows_no_results_message -v -s
```

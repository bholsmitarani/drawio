"""
test_kendo_poc.py — FIXED v4
Key discoveries from logs:
1. Search input: 'NOT FOUND' means span.k-input.k-textbox selector is wrong
   Kendo Input in this version uses span.k-input (without k-textbox)
   Fix: use broader selector + find by placeholder
2. test_03 fails because test_02 failed to type — search never ran
   Fix: type directly in test_03 using the correct selector
3. test_08: same input selector issue

Run:
    python -m pytest test_kendo_poc.py -v -s
"""

import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class KendoTestIdInjector:

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait   = WebDriverWait(driver, timeout)

    def inject_all(self):
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        self._inject_inputs()
        self._inject_dropdowns()
        self._inject_numerics()
        self._inject_datepickers()
        self._inject_buttons()
        self._inject_grid_rows()
        print("\n[INJECTOR] Done.")
        self._print_all()

    def _inject_inputs(self):
        """
        Kendo Input: try multiple span selectors to find the wrapper.
        Then tag the inner native input with the id as testid.
        Also inject directly by placeholder as fallback.
        """
        self.driver.execute_script("""
            // Try all possible Kendo input wrapper classes
            var selectors = [
                'span.k-input.k-textbox',
                'span.k-textbox',
                'span.k-input:not(.k-dropdownlist):not(.k-numerictextbox):not(.k-datepicker)'
            ];
            var found = new Set();
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(span => {
                    if (!found.has(span)) {
                        found.add(span);
                        var inner  = span.querySelector('input');
                        if (!inner) return;
                        var baseId = inner.id || span.id || ('kendo-input-' + found.size);
                        if (!span.getAttribute('data-testid'))
                            span.setAttribute('data-testid', baseId + '-wrapper');
                        if (!inner.getAttribute('data-testid'))
                            inner.setAttribute('data-testid', baseId);
                    }
                });
            });

            // Fallback: tag by placeholder directly
            var searchInput = document.querySelector('input[placeholder="Enter name..."]');
            if (searchInput && !searchInput.getAttribute('data-testid')) {
                searchInput.setAttribute('data-testid', 'search-input-native');
            }
        """)

        # Debug: show ALL inputs on page and their testids
        result = self.driver.execute_script("""
            return Array.from(document.querySelectorAll('input')).map(el => ({
                id:          el.id,
                placeholder: el.placeholder,
                type:        el.type,
                testid:      el.getAttribute('data-testid'),
                parentClass: el.parentElement ? el.parentElement.className : ''
            }));
        """)
        print("\n[DEBUG] All inputs on page:")
        for r in result:
            print(f"  id={r['id']} | placeholder={r['placeholder']} | testid={r['testid']} | parentClass={r['parentClass'][:60]}")

    def _inject_dropdowns(self):
        self.driver.execute_script("""
            var names = ['role-dropdown', 'status-dropdown'];
            document.querySelectorAll('span.k-dropdownlist').forEach((el, i) => {
                if (!el.getAttribute('data-testid'))
                    el.setAttribute('data-testid', names[i] || ('kendo-dropdown-' + i));
            });
        """)

    def _inject_numerics(self):
        self.driver.execute_script("""
            document.querySelectorAll('span.k-numerictextbox').forEach((el, i) => {
                var inner  = el.querySelector('input');
                var baseId = (inner && inner.id) ? inner.id : ('kendo-numeric-' + i);
                if (!el.getAttribute('data-testid'))
                    el.setAttribute('data-testid', baseId + '-wrapper');
                if (inner && !inner.getAttribute('data-testid'))
                    inner.setAttribute('data-testid', baseId);
            });
        """)

    def _inject_datepickers(self):
        self.driver.execute_script("""
            document.querySelectorAll('span.k-datepicker').forEach((el, i) => {
                var inner  = el.querySelector('input');
                var baseId = (inner && inner.id) ? inner.id : ('kendo-datepicker-' + i);
                if (!el.getAttribute('data-testid'))
                    el.setAttribute('data-testid', baseId + '-wrapper');
                if (inner && !inner.getAttribute('data-testid'))
                    inner.setAttribute('data-testid', baseId);
            });
        """)

    def _inject_buttons(self):
        self.driver.execute_script("""
            document.querySelectorAll('button.k-button').forEach((el) => {
                if (!el.getAttribute('data-testid')) {
                    var label = el.innerText.trim()
                        .toLowerCase()
                        .replace(/[^a-z0-9]+/g, '-')
                        .replace(/^-|-$/g, '');
                    el.setAttribute('data-testid', 'kendo-btn-' + label);
                }
            });
        """)

    def _inject_grid_rows(self):
        self.driver.execute_script("""
            document.querySelectorAll('div.k-grid').forEach((grid, gi) => {
                var gid = 'kendo-grid-' + gi;
                if (!grid.getAttribute('data-testid'))
                    grid.setAttribute('data-testid', gid);
                grid.querySelectorAll('tbody tr').forEach((row, ri) => {
                    row.setAttribute('data-testid', gid + '-row-' + ri);
                    row.querySelectorAll('td').forEach((cell, ci) => {
                        cell.setAttribute('data-testid', gid + '-cell-' + ri + '-' + ci);
                    });
                });
            });
        """)

    def get_search_input(self):
        """
        Find the search input element using multiple strategies.
        Returns the element directly, not just the testid.
        """
        # Strategy 1: by placeholder
        els = self.driver.find_elements(
            By.CSS_SELECTOR, 'input[placeholder="Enter name..."]'
        )
        if els:
            print(f"\n[INJECTOR] Found search input by placeholder. testid={els[0].get_attribute('data-testid')}")
            return els[0]

        # Strategy 2: by injected testid variants
        for testid in ['searchBox', 'search-input-native', 'kendo-input-0']:
            els = self.driver.find_elements(
                By.CSS_SELECTOR, f"[data-testid='{testid}']"
            )
            if els and els[0].tag_name == 'input':
                print(f"\n[INJECTOR] Found search input by testid={testid}")
                return els[0]

        # Strategy 3: first visible input on page
        for el in self.driver.find_elements(By.TAG_NAME, 'input'):
            if el.is_displayed() and el.get_attribute('type') != 'hidden':
                print(f"\n[INJECTOR] Found search input as first visible input. id={el.get_attribute('id')}")
                return el

        raise Exception("Search input not found by any strategy")

    def _print_all(self):
        result = self.driver.execute_script("""
            return Array.from(document.querySelectorAll('[data-testid]'))
                .map(el => el.tagName + ' -> ' + el.getAttribute('data-testid'));
        """)
        print(f"\n[INJECTOR] {len(result)} testids on page:")
        for r in result:
            print("  ", r)


def select_kendo_dropdown(driver, testid, option_text):
    wait = WebDriverWait(driver, 10)
    dd = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, f"[data-testid='{testid}']")
    ))
    dd.click()
    time.sleep(0.5)
    items = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, ".k-list-item")
    ))
    for item in items:
        if item.text.strip() == option_text:
            item.click()
            return
    raise ValueError(f"Option '{option_text}' not found in '{testid}'")


@pytest.fixture(scope="session")
def driver():
    opts = Options()
    opts.add_argument("--start-maximized")
    d = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )
    d.get("http://localhost:5173")
    yield d
    d.quit()


@pytest.fixture(scope="session", autouse=True)
def inject(driver):
    inj = KendoTestIdInjector(driver)
    inj.inject_all()
    return inj


class TestKendoPoCApp:

    def test_01_page_loads(self, driver):
        h1 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.TAG_NAME, "h1"))
        )
        assert "KendoReact" in h1.text
        print(f"\n[PASS] Title: {h1.text}")

    def test_02_search_input_accepts_text(self, driver, inject):
        """Use multi-strategy finder instead of hardcoded testid."""
        native = inject.get_search_input()
        native.click()
        native.send_keys(Keys.CONTROL + "a")
        native.send_keys("Alice")
        time.sleep(0.3)
        val = native.get_attribute("value")
        assert val == "Alice", f"Expected 'Alice', got '{val}'"
        print(f"\n[PASS] Search input value: {val}")

    def test_03_search_filters_grid(self, driver, inject):
        wait = WebDriverWait(driver, 10)

        # Make sure search text is set
        native = inject.get_search_input()
        native.click()
        native.send_keys(Keys.CONTROL + "a")
        native.send_keys("Alice")
        time.sleep(0.3)

        # Click Search
        btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[data-testid='kendo-btn-search']")
        ))
        btn.click()
        time.sleep(1.0)

        # Re-inject rows
        inject._inject_grid_rows()
        time.sleep(0.3)

        rows = driver.find_elements(
            By.CSS_SELECTOR, "div.k-grid tbody tr[data-testid]"
        )
        assert len(rows) == 1, f"Expected 1, got {len(rows)}"
        print(f"\n[PASS] Grid filtered to {len(rows)} row")

    def test_04_role_dropdown_selects_manager(self, driver):
        select_kendo_dropdown(driver, "role-dropdown", "Manager")
        time.sleep(0.3)
        val = driver.find_element(
            By.CSS_SELECTOR, "[data-testid='role-dropdown'] .k-input-value-text"
        ).text
        assert val == "Manager"
        print(f"\n[PASS] Role: {val}")

        #Status dropdown had no id, no testid, no placeholder in the source code. 
        #The injector will find it purely by position (span.k-dropdownlist:nth) and give it a stable testid. 
    def test_05_status_dropdown_no_id(self, driver):
        select_kendo_dropdown(driver, "status-dropdown", "Inactive")
        time.sleep(0.3)
        val = driver.find_element(
            By.CSS_SELECTOR, "[data-testid='status-dropdown'] .k-input-value-text"
        ).text
        assert val == "Inactive"
        print(f"\n[PASS] Status (no original id): {val}")

    def test_06_numeric_age_input(self, driver):
        wait   = WebDriverWait(driver, 10)
        native = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-testid='ageInput']")
        ))
        driver.execute_script("arguments[0].select();", native)
        native.send_keys("30")
        time.sleep(0.3)
        assert "30" in native.get_attribute("value")
        print("\n[PASS] Age set to 30")

    def test_07_submit_shows_banner(self, driver):
        wait = WebDriverWait(driver, 10)
        btn  = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[data-testid='kendo-btn-submit']")
        ))
        btn.click()
        time.sleep(0.8)
        driver.execute_script("""
            document.querySelectorAll('section.userForm > div').forEach(div => {
                if (div.innerText && div.innerText.includes('Submitted'))
                    div.setAttribute('data-testid', 'submit-confirmation');
            });
        """)
        banner = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "[data-testid='submit-confirmation']")
        ))
        assert "Manager" in banner.text
        print(f"\n[PASS] Banner: {banner.text[:60]}")

    def test_08_reset_clears_form(self, driver, inject):
        wait = WebDriverWait(driver, 10)
        btn  = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[data-testid='kendo-btn-reset']")
        ))
        btn.click()
        time.sleep(0.8)

        native = inject.get_search_input()
        val = native.get_attribute("value")
        assert val == "", f"Expected empty, got '{val}'"
        print("\n[PASS] Reset cleared form")

    def test_09_grid_shows_all_after_reset(self, driver, inject):
        time.sleep(0.5)
        inject._inject_grid_rows()
        time.sleep(0.3)
        rows = driver.find_elements(
            By.CSS_SELECTOR, "div.k-grid tbody tr[data-testid]"
        )
        assert len(rows) == 4, f"Expected 4, got {len(rows)}"
        print(f"\n[PASS] Grid shows {len(rows)} rows after reset")

    def test_10_grid_first_row_name(self, driver):
        cell = driver.find_element(
            By.CSS_SELECTOR, "[data-testid='kendo-grid-0-cell-0-1']"
        )
        assert "Alice" in cell.text
        print(f"\n[PASS] Row 0 name: {cell.text}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
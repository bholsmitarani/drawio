"""
kendo_testid_injector.py
========================
Dynamically injects data-testid attributes into KendoReact components
BEFORE running Selenium tests — when the app has no test IDs built in.

Strategy:
  1. Identify Kendo components by their stable CSS class names (k-*)
  2. Inject data-testid via JavaScript
  3. Use those testids in all subsequent Selenium interactions

Usage:
  from kendo_testid_injector import KendoTestIdInjector
  injector = KendoTestIdInjector(driver)
  injector.inject_all()
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


class KendoTestIdInjector:
    """
    Injects data-testid attributes into KendoReact components at runtime.
    Call inject_all() once after page load, before any test interactions.
    """

    def __init__(self, driver: webdriver.Chrome, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ─────────────────────────────────────────────────────────────
    # CORE: Run any JS injection on the page
    # ─────────────────────────────────────────────────────────────

    def _inject_js(self, script: str):
        """Execute a JavaScript snippet to inject data-testid attributes."""
        self.driver.execute_script(script)

    # ─────────────────────────────────────────────────────────────
    # INJECT ALL — call this once after page load
    # ─────────────────────────────────────────────────────────────

    def inject_all(self):
        """
        Master method: inject data-testid into all known Kendo components.
        Call this ONCE after navigating to the page.
        """
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(1)  # allow Kendo components to fully render

        self.inject_text_inputs()
        self.inject_dropdowns()
        self.inject_numeric_boxes()
        self.inject_datepickers()
        self.inject_buttons()
        self.inject_grids()
        self.inject_checkboxes()
        self.inject_radiobuttons()
        self.inject_multiselect()
        self.inject_combobox()
        self.inject_timepicker()
        self.inject_slider()

        print("[KendoInjector] data-testid injection complete.")

    # ─────────────────────────────────────────────────────────────
    # INDIVIDUAL COMPONENT INJECTORS
    # ─────────────────────────────────────────────────────────────

    def inject_text_inputs(self):
        """
        Kendo Input renders: <span class="k-input k-textbox"> <input ...> </span>
        We inject data-testid on the outer span AND inner input.
        """
        self._inject_js("""
            document.querySelectorAll('span.k-input.k-textbox, span.k-input-inner').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    var testId = el.id || ('kendo-input-' + i);
                    el.setAttribute('data-testid', testId);
                    // also tag the inner native input
                    var inner = el.querySelector('input');
                    if (inner && !inner.getAttribute('data-testid')) {
                        inner.setAttribute('data-testid', testId + '-native');
                    }
                }
            });
        """)
        print("[Injected] Text Inputs")

    def inject_dropdowns(self):
        """
        Kendo DropDownList renders: <span class="k-dropdownlist k-picker">
        We inject on the wrapper span — this is what Selenium clicks to open.
        """
        self._inject_js("""
            document.querySelectorAll('span.k-dropdownlist').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    var testId = el.id || ('kendo-dropdown-' + i);
                    el.setAttribute('data-testid', testId);
                }
            });
        """)
        print("[Injected] DropDownLists")

    def inject_numeric_boxes(self):
        """
        Kendo NumericTextBox renders: <span class="k-numerictextbox">
        We inject on wrapper and inner input.
        """
        self._inject_js("""
            document.querySelectorAll('span.k-numerictextbox').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    var testId = el.id || ('kendo-numeric-' + i);
                    el.setAttribute('data-testid', testId);
                    var inner = el.querySelector('input');
                    if (inner && !inner.getAttribute('data-testid')) {
                        inner.setAttribute('data-testid', testId + '-native');
                    }
                }
            });
        """)
        print("[Injected] NumericTextBoxes")

    def inject_datepickers(self):
        """
        Kendo DatePicker renders: <span class="k-datepicker">
        """
        self._inject_js("""
            document.querySelectorAll('span.k-datepicker').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    var testId = el.id || ('kendo-datepicker-' + i);
                    el.setAttribute('data-testid', testId);
                    var inner = el.querySelector('input');
                    if (inner && !inner.getAttribute('data-testid')) {
                        inner.setAttribute('data-testid', testId + '-native');
                    }
                }
            });
        """)
        print("[Injected] DatePickers")

    def inject_buttons(self):
        """
        Kendo Button renders: <button class="k-button">
        We use button text as part of testid for readability.
        """
        self._inject_js("""
            document.querySelectorAll('button.k-button').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    var label = el.innerText.trim()
                        .toLowerCase()
                        .replace(/[^a-z0-9]+/g, '-')
                        .replace(/^-|-$/g, '');
                    var testId = el.id || ('kendo-btn-' + (label || i));
                    el.setAttribute('data-testid', testId);
                }
            });
        """)
        print("[Injected] Buttons")

    def inject_grids(self):
        """
        Kendo Grid renders: <div class="k-grid">
        We inject on the grid wrapper and also tag each row.
        """
        self._inject_js("""
            document.querySelectorAll('div.k-grid').forEach((grid, gi) => {
                if (!grid.getAttribute('data-testid')) {
                    var testId = grid.id || ('kendo-grid-' + gi);
                    grid.setAttribute('data-testid', testId);
                }
                // tag each data row
                grid.querySelectorAll('tbody tr').forEach((row, ri) => {
                    if (!row.getAttribute('data-testid')) {
                        var gridId = grid.getAttribute('data-testid');
                        row.setAttribute('data-testid', gridId + '-row-' + ri);
                        // tag each cell
                        row.querySelectorAll('td').forEach((cell, ci) => {
                            cell.setAttribute('data-testid', gridId + '-row-' + ri + '-col-' + ci);
                        });
                    }
                });
            });
        """)
        print("[Injected] Grids + rows + cells")

    def inject_checkboxes(self):
        """Kendo Checkbox: input[type=checkbox] inside k-checkbox-wrap"""
        self._inject_js("""
            document.querySelectorAll('input[type="checkbox"].k-checkbox').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    el.setAttribute('data-testid', el.id || ('kendo-checkbox-' + i));
                }
            });
        """)
        print("[Injected] Checkboxes")

    def inject_radiobuttons(self):
        """Kendo RadioButton: input[type=radio].k-radio"""
        self._inject_js("""
            document.querySelectorAll('input[type="radio"].k-radio').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    el.setAttribute('data-testid', el.id || ('kendo-radio-' + i));
                }
            });
        """)
        print("[Injected] RadioButtons")

    def inject_multiselect(self):
        """Kendo MultiSelect: div.k-multiselect"""
        self._inject_js("""
            document.querySelectorAll('div.k-multiselect').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    el.setAttribute('data-testid', el.id || ('kendo-multiselect-' + i));
                }
            });
        """)
        print("[Injected] MultiSelects")

    def inject_combobox(self):
        """Kendo ComboBox: span.k-combobox"""
        self._inject_js("""
            document.querySelectorAll('span.k-combobox').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    el.setAttribute('data-testid', el.id || ('kendo-combobox-' + i));
                }
            });
        """)
        print("[Injected] ComboBoxes")

    def inject_timepicker(self):
        """Kendo TimePicker: span.k-timepicker"""
        self._inject_js("""
            document.querySelectorAll('span.k-timepicker').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    el.setAttribute('data-testid', el.id || ('kendo-timepicker-' + i));
                }
            });
        """)
        print("[Injected] TimePickers")

    def inject_slider(self):
        """Kendo Slider: div.k-slider"""
        self._inject_js("""
            document.querySelectorAll('div.k-slider').forEach((el, i) => {
                if (!el.getAttribute('data-testid')) {
                    el.setAttribute('data-testid', el.id || ('kendo-slider-' + i));
                }
            });
        """)
        print("[Injected] Sliders")

    # ─────────────────────────────────────────────────────────────
    # INJECT CUSTOM MAPPING — for apps with known structure
    # ─────────────────────────────────────────────────────────────

    def inject_custom_mapping(self, mapping: dict):
        """
        Inject data-testid using a custom CSS selector → testid mapping.
        Use this when you know the page structure but there are no IDs.

        Example:
            mapping = {
                "form div:nth-child(1) span.k-dropdownlist": "patient-status-dropdown",
                "form div:nth-child(2) span.k-datepicker":   "admission-date-picker",
                "table.k-grid":                              "patient-grid",
            }
            injector.inject_custom_mapping(mapping)
        """
        for selector, testid in mapping.items():
            self._inject_js(f"""
                var el = document.querySelector('{selector}');
                if (el) {{
                    el.setAttribute('data-testid', '{testid}');
                    console.log('[Injected] {testid} on {selector}');
                }} else {{
                    console.warn('[KendoInjector] Not found: {selector}');
                }}
            """)
        print(f"[Injected] Custom mapping: {len(mapping)} elements")

    # ─────────────────────────────────────────────────────────────
    # VERIFY — confirm injection worked
    # ─────────────────────────────────────────────────────────────

    def verify_injection(self, testid: str) -> bool:
        """Check if a data-testid was successfully injected."""
        elements = self.driver.find_elements(
            By.CSS_SELECTOR, f"[data-testid='{testid}']"
        )
        found = len(elements) > 0
        status = "FOUND" if found else "NOT FOUND"
        print(f"[Verify] data-testid='{testid}' → {status}")
        return found

    def get_all_injected_testids(self) -> list:
        """Return a list of all data-testid values currently on the page."""
        result = self.driver.execute_script("""
            return Array.from(document.querySelectorAll('[data-testid]'))
                        .map(el => ({
                            tag:     el.tagName,
                            testid:  el.getAttribute('data-testid'),
                            classes: el.className
                        }));
        """)
        print(f"[Verify] Total elements with data-testid: {len(result)}")
        for item in result:
            print(f"  <{item['tag']}> testid='{item['testid']}'")
        return result


# ─────────────────────────────────────────────────────────────────
# EXAMPLE USAGE IN A TEST
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from selenium.webdriver.chrome.options import Options

    options = Options()
    # options.add_argument("--headless")  # uncomment for headless
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("http://localhost:5173")

        # ── Step 1: Inject data-testid into all Kendo components ──
        injector = KendoTestIdInjector(driver)
        injector.inject_all()

        # ── Step 2: Optionally inject custom mapping for known fields ──
        # injector.inject_custom_mapping({
        #     "form div:nth-child(1) span.k-dropdownlist": "patient-status-dropdown",
        # })

        # ── Step 3: Verify injection ──
        injector.verify_injection("kendo-dropdown-0")
        injector.verify_injection("kendo-grid-0")
        all_ids = injector.get_all_injected_testids()

        # ── Step 4: Now use data-testid in your tests ──
        wait = WebDriverWait(driver, 10)

        # Click dropdown (auto-injected testid)
        dropdown = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[data-testid='kendo-dropdown-0']")
        ))
        dropdown.click()
        time.sleep(0.5)

        # Pick an option from popup
        options_list = driver.find_elements(By.CSS_SELECTOR, ".k-list-item")
        for opt in options_list:
            if opt.text == "Manager":
                opt.click()
                break

        # Click submit button (auto-injected from button text)
        submit_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[data-testid='kendo-btn-submit']")
        ))
        submit_btn.click()

        print("\n[TEST PASSED] Injection + interaction complete.")
        time.sleep(2)

    finally:
        driver.quit()

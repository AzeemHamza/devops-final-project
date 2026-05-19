import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "http://localhost:3000"   # change to AKS IP if testing cloud

# Generate unique credentials to avoid "user already exists"
unique_id = int(time.time())
USERNAME = f"testuser{unique_id}"
EMAIL = f"test{unique_id}@example.com"
PASSWORD = "Test1234"

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def js_click(driver, element):
    """Click an element using JavaScript, bypassing overlapping elements."""
    driver.execute_script("arguments[0].click();", element)

def find_by_label(driver, label_text):
    return driver.find_element(By.XPATH,
        f"//div[contains(@class,'MuiFormControl-root')][.//label[text()='{label_text}']]//input"
    )

def find_select_by_label(driver, label_text):
    return driver.find_element(By.XPATH,
        f"//div[contains(@class,'MuiFormControl-root')][.//label[text()='{label_text}']]//div[contains(@class,'MuiInputBase-root')]"
    )

def wait_for_label(driver, label_text, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH,
            f"//div[contains(@class,'MuiFormControl-root')][.//label[text()='{label_text}']]//input"
        ))
    )

def test_register_and_login():
    driver = create_driver()
    try:
        # ---------- Register ----------
        driver.get(f"{URL}/register")
        wait_for_label(driver, "Username").send_keys(USERNAME)
        find_by_label(driver, "Email").send_keys(EMAIL)
        find_by_label(driver, "Password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        # Wait for dashboard (max 15 seconds, just in case)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(),'Your Tasks')]"))
        )
        print("✅ Registration successful, dashboard loaded.")

        # Wait for snackbar to disappear
        try:
            WebDriverWait(driver, 8).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "notistack-MuiContent"))
            )
        except:
            pass
        time.sleep(0.5)

        # ---------- Logout ----------
        logout_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Logout')]")
        js_click(driver, logout_btn)

        # Wait for login page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(),'Welcome Back')]"))
        )
        print("✅ Logout successful.")

        # ---------- Login ----------
        find_by_label(driver, "Email").send_keys(EMAIL)
        find_by_label(driver, "Password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(),'Your Tasks')]"))
        )
        print("✅ Login successful.")
    finally:
        driver.quit()

def test_add_and_toggle_item():
    driver = create_driver()
    try:
        # Login with the unique user
        driver.get(f"{URL}/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'MuiFormControl-root')][.//label[text()='Email']]//input"))
        )
        find_by_label(driver, "Email").send_keys(EMAIL)
        find_by_label(driver, "Password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(),'Your Tasks')]"))
        )

        # Add item
        wait_for_label(driver, "New Task").send_keys("Selenium Task")
        cat_select = find_select_by_label(driver, "Category")
        cat_select.click()
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@data-value='Work']"))
        ).click()
        driver.find_element(By.XPATH, "//input[@type='date']").send_keys("12/25/2026")
        add_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Add')]")
        js_click(driver, add_btn)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h6[contains(text(),'Selenium Task')]"))
        )
        print("✅ Item added.")

        # Toggle checkbox
        checkbox = driver.find_element(By.XPATH,
            "//h6[contains(text(),'Selenium Task')]/ancestor::div[contains(@class,'MuiCard-root')]//input[@type='checkbox']"
        )
        js_click(driver, checkbox)
        time.sleep(1)
        assert checkbox.is_selected()
        print("✅ Toggle completion works.")
    finally:
        driver.quit()

def test_delete_item():
    driver = create_driver()
    try:
        # Login
        driver.get(f"{URL}/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'MuiFormControl-root')][.//label[text()='Email']]//input"))
        )
        find_by_label(driver, "Email").send_keys(EMAIL)
        find_by_label(driver, "Password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(),'Your Tasks')]"))
        )

        # Wait for any lingering snackbar to disappear
        try:
            WebDriverWait(driver, 5).until_not(
                EC.presence_of_element_located((By.CLASS_NAME, "notistack-MuiContent"))
            )
        except:
            pass

        # Delete the item
        delete_btn = driver.find_element(By.XPATH,
            "//h6[contains(text(),'Selenium Task')]/ancestor::div[contains(@class,'MuiCard-root')]//button[.//*[name()='svg' and @data-testid='DeleteIcon']]"
        )
        js_click(driver, delete_btn)
        time.sleep(1)
        items = driver.find_elements(By.XPATH, "//h6[contains(text(),'Selenium Task')]")
        assert len(items) == 0
        print("✅ Delete item works.")
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Running TaskFlow Pro tests...")
    print(f"Using unique user: {USERNAME} / {EMAIL}")
    test_register_and_login()
    test_add_and_toggle_item()
    test_delete_item()
    print("✅ All tests passed.")
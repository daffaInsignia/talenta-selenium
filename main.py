import os
import shutil
import sys
import tempfile
import time

from dotenv import load_dotenv
from os import environ

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

TALENTA_URL = "https://hr.talenta.co/live-attendance"
WAIT_TIMEOUT = 20


def load_config() -> dict[str, str]:
    load_dotenv()
    required = ["TALENTA_EMAIL", "TALENTA_PASSWORD"]
    config: dict[str, str] = {}
    for key in required:
        val = environ.get(key, "")
        if not val:
            print(f"Error: {key} harus diisi di .env")
            sys.exit(1)
        config[key] = val
    config["CLOCK_IN_TIME"] = environ.get("CLOCK_IN_TIME", "09:00")
    config["CLOCK_OUT_TIME"] = environ.get("CLOCK_OUT_TIME", "18:00")
    config["LATITUDE"] = environ.get("LATITUDE", "")
    config["LONGITUDE"] = environ.get("LONGITUDE", "")
    return config


def create_driver() -> webdriver.Chrome:
    options = Options()
    is_headless = environ.get("HEADLESS", "").lower() in ("1", "true", "yes")
    temp_dir = None

    if is_headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-gpu-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--remote-debugging-pipe")
        options.add_argument("--window-size=1920,1080")
        
        # Use a generic but modern user agent
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        )
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        temp_dir = tempfile.mkdtemp(prefix="talenta-chrome-")
        options.add_argument(f"--user-data-dir={temp_dir}")
    else:
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        })

    log_path = os.path.join(os.path.dirname(__file__), "chromedriver.log")
    service = Service(log_output=log_path)
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        if is_headless:
            driver._temp_profile_dir = temp_dir
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
            )
        return driver
    except Exception as e:
        print(f"[driver] Failed to initialize: {e}", flush=True)
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def set_geolocation(driver: webdriver.Chrome, lat: str, lng: str) -> None:
    if not lat or not lng:
        return
    params = {
        "latitude": float(lat),
        "longitude": float(lng),
        "accuracy": 100,
    }
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)
    driver.execute_cdp_cmd("Browser.grantPermissions", {
        "permissions": ["geolocation"],
    })
    print(f"[geo] Location set to {lat}, {lng}", flush=True)


def dismiss_popups(driver: webdriver.Chrome) -> None:
    time.sleep(2)
    close_selectors = [
        (By.CSS_SELECTOR, "button.close"),
        (By.CSS_SELECTOR, "[aria-label='Close']"),
        (By.CSS_SELECTOR, "button[data-dismiss='modal']"),
        (By.CSS_SELECTOR, "button[data-bs-dismiss='modal']"),
        (By.XPATH, "//button[contains(text(), '×')]"),
        (By.XPATH, "//span[contains(text(), '×')]/.."),
    ]
    for by, selector in close_selectors:
        try:
            for el in driver.find_elements(by, selector):
                if el.is_displayed():
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(0.5)
        except Exception:
            continue
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(1)
    except Exception:
        pass


def login(driver: webdriver.Chrome, email: str, password: str) -> None:
    print("[login] Opening Talenta...", flush=True)
    driver.get(TALENTA_URL)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    email_field = wait.until(EC.presence_of_element_located((By.ID, "user_email")))
    email_field.clear()
    email_field.send_keys(email)

    password_field = wait.until(EC.presence_of_element_located((By.ID, "user_password")))
    password_field.clear()
    password_field.send_keys(password)

    login_btn = wait.until(EC.element_to_be_clickable((By.ID, "new-signin-button")))
    driver.execute_script("arguments[0].click();", login_btn)
    print("[login] Credentials submitted, waiting for redirect...", flush=True)

    WebDriverWait(driver, 30).until(EC.url_contains("hr.talenta.co"))
    print(f"[login] Logged in -> {driver.current_url}", flush=True)

    dismiss_popups(driver)


def navigate_to_live_attendance(driver: webdriver.Chrome) -> None:
    driver.get(TALENTA_URL)
    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.url_contains("/live-attendance"))
    time.sleep(3)
    dismiss_popups(driver)
    print(f"[nav] Live attendance loaded: {driver.current_url}", flush=True)


def click_clock_button(driver: webdriver.Chrome, action: str) -> bool:
    """Click 'Clock In' or 'Clock Out' button. Returns True if successful."""
    button_text = "Clock In" if action == "clock_in" else "Clock Out"
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    try:
        btn = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//button[normalize-space()='{button_text}']")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", btn)
        print(f"[clock] Clicked '{button_text}'", flush=True)
        time.sleep(3)

        driver.save_screenshot(f"screenshots/after_{action}.png")
        print(f"[clock] Screenshot saved: screenshots/after_{action}.png", flush=True)
        return True
    except TimeoutException:
        print(f"[clock] Button '{button_text}' not found or not clickable", flush=True)
        driver.save_screenshot(f"screenshots/fail_{action}.png")
        return False


def perform_attendance(action: str) -> bool:
    """Full flow: login -> navigate -> click clock button. Returns True if successful."""
    config = load_config()
    driver = None
    try:
        driver = create_driver()
        set_geolocation(driver, config["LATITUDE"], config["LONGITUDE"])
        login(driver, config["TALENTA_EMAIL"], config["TALENTA_PASSWORD"])
        navigate_to_live_attendance(driver)
        return click_clock_button(driver, action)
    except Exception as e:
        print(f"[error] {type(e).__name__}: {e}", flush=True)
        if driver:
            try:
                driver.save_screenshot(f"screenshots/error_{action}.png")
            except Exception:
                pass
        return False
    finally:
        if driver:
            temp_dir = getattr(driver, "_temp_profile_dir", None)
            try:
                driver.quit()
            except Exception:
                pass
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    import os
    os.makedirs("screenshots", exist_ok=True)

    action = sys.argv[1] if len(sys.argv) > 1 else "clock_in"
    if action not in ("clock_in", "clock_out"):
        print(f"Usage: python main.py [clock_in|clock_out]")
        sys.exit(1)

    success = perform_attendance(action)
    sys.exit(0 if success else 1)

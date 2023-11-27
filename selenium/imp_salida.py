# Selenium and related imports
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire.undetected_chromedriver import webdriver as uc

# Third-party libraries for enhanced web scraping
from selectolax.parser import HTMLParser
from fake_useragent import UserAgent
from selenium_stealth import stealth

# Data handling and utility tools
from dataclasses import dataclass, asdict
from pprint import pprint

# CLI tools and custom modules
from click import command, option
from recaptchaSolver import recaptchaSolver
import crawlab

import time


PROXY_HTTP = "http://customer-ecuachecks-cc-ec-sessid-0620968049-sesstime-3:Ecuachecks2023@pr.oxylabs.io:7777"
PROXY_HTTPS = "https://customer-ecuachecks-cc-ec-sessid-0620968049-sesstime-3:Ecuachecks2023@pr.oxylabs.io:7777"
USER_AGENT = UserAgent(os=["windows"], min_percentage=15.0).random
URL = "https://impedimentos.migracion.gob.ec/simiec-consultaImpedimentos/"


def setup_driver():
    # Settings of undetected_chromedriver to avoid detection
    options = uc.ChromeOptions()
    # options.add_argument('--headless=new')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-plugins-discovery")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--ignore-ssl-errors=yes")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--user-agent={USER_AGENT}")

    service = Service(ChromeDriverManager().install())

    wire_options = {
        "connection_timeout": None,  # Wait forever for the connection to start
        "connection_keep_alive": True,  # Use connection keep-alive
        "proxy": {"http": PROXY_HTTP, "https": PROXY_HTTPS},
    }

    # Setup driver
    driver = uc.Chrome(
        service=service,
        options=options,
        seleniumwire_options=wire_options
        # version_main=106
    )

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    stealth(
        driver,
        user_agent=USER_AGENT,
        languages=["es-EC", "es"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver


def get_html(driver):
    try:
        driver.get(URL)
        result = recaptchaSolver("6Ld38BkUAAAAAPATwit3FXvga1PI6iVTb6zgXw62", URL)
        code = result.get("code")
        print(code)
        frames = driver.find_elements(By.TAG_NAME, "iframe")

        for frame in frames:
            driver.switch_to.frame(frame)
            try:
                captcha_box = driver.find_element(By.CLASS_NAME, "g-recaptcha")
                if captcha_box:
                    break
            except:
                driver.switch_to.default_content()

        driver.execute_script(f"onCaptchaFinished('{code}')")
        driver.switch_to.default_content()
        time.sleep(900)

    finally:
        driver.quit()


def run():
    driver = setup_driver()
    get_html(driver)


if __name__ == "__main__":
    run()

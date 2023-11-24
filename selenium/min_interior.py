# Selenium and related imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

# Third-party libraries for enhanced web scraping
from selectolax.parser import HTMLParser
from fake_useragent import UserAgent
from selenium_stealth import stealth

# Data handling and utility tools
from typing import Generator
from dataclasses import dataclass, asdict
from pprint import pprint

# CLI tools and custom modules
from click import command, option
from recaptchaSolver import recaptchaSolver
import crawlab

import time

PROXY_HTTP = "http://customer-ecuachecks-cc-ec:Ecuachecks2023@pr.oxylabs.io:7777"
PROXY_HTTPS = "https://customer-ecuachecks-cc-ec:Ecuachecks2023@pr.oxylabs.io:7777"
USER_AGENT = UserAgent(os=["windows"], min_percentage=15.0).random
URL = "https://certificados.ministeriodelinterior.gob.ec/gestorcertificados/antecedentes/"


@dataclass
class MinInteriorItem:
    name: str
    id_number: str
    doc_type: str
    background: str
    certificate: str


def setup_driver():

    # Settings of undetected_chromedriver to avoid detection
    options = uc.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--incognito')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--no-sandbox')
    options.add_argument(f'user-agent={USER_AGENT}')

    wire_options = {
        'connection_timeout': None,  # Wait forever for the connection to start
        'connection_keep_alive': True,  # Use connection keep-alive
        'proxy': {
            'http': PROXY_HTTP,
            'https': PROXY_HTTPS
        },
    }

    # Setup driver
    driver = uc.Chrome(
        options=options,
        seleniumwire_options=wire_options,
        # version_main=106
    )

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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


def get_html(driver: uc.Chrome, search_id: str):
    try:
        driver.get(URL)
        result = recaptchaSolver(
            "6Ld38BkUAAAAAPATwit3FXvga1PI6iVTb6zgXw62",
            URL
        )
        code = result.get('code')
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

        time.sleep(5)

        driver.find_element(
            By.XPATH, "//button/span[text()='Aceptar']").click()

        time.sleep(7)

        driver.find_element(By.ID, 'txtCi').send_keys(search_id)

        siguiente_button = driver.find_element(By.ID, 'btnSig1')
        siguiente_button.click()

        time.sleep(7)

        motivo_textarea = driver.find_element(By.ID, 'txtMotivo')
        motivo_textarea.clear()
        motivo_textarea.send_keys("Consulta de antecedentes")

        driver.find_element(By.ID, 'btnSig2').click()
        time.sleep(5)

        parser = HTMLParser(driver.page_source)

        driver.find_element(By.ID, 'btnOpen').click()
        time.sleep(5)
        driver.switch_to.window(driver.window_handles[-1])

        cert_url = driver.current_url

        return (parser, cert_url)

    except Exception as e:
        print(e)
        driver.quit()


def parse_data(parser: HTMLParser, cert_url: str):
    item = MinInteriorItem(
        name=parser.css_first('#dvName1').text(strip=True),
        id_number=parser.css_first('#dvType1').text(strip=True),
        doc_type=parser.css_first('#dvCi1').text(strip=True),
        background=parser.css_first(
            '#dvAntecedent1').text(strip=True),
        certificate=cert_url
    )

    dict_item = asdict(item)
    crawlab.save_item(dict_item)
    pprint(dict_item)


if __name__ == "__main__":
    driver = setup_driver()
    data, cert = get_html(driver, "1725514119")
    parse_data(data, cert)

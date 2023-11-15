from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

from selectolax.parser import HTMLParser
from fake_useragent import UserAgent
from selenium_stealth import stealth
import time


def setup_driver():
    # Configuraciones de undetected_chromedriver para evitar la detección
    USER_AGENT = UserAgent(os=["windows"], min_percentage=15.0).random

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless=new')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--incognito')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument(f'user-agent={USER_AGENT}')

    wire_options = {
        'connection_timeout': None,  # Wait forever for the connection to start
        'connection_keep_alive': True,  # Use connection keep-alive
        'proxy': {
            'http': "http://customer-ecuachecks-cc-ec-sessid-0519303614-sesstime-5:Ecuachecks2023@pr.oxylabs.io:7777",
            'https': "https://customer-ecuachecks-cc-ec-sessid-0519303614-sesstime-5:Ecuachecks2023@pr.oxylabs.io:7777"
        },
    }

    # Crear el driver con las opciones
    driver = webdriver.Chrome(
        options=options,
        seleniumwire_options=wire_options
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

    driver.implicitly_wait(3)

    return driver


def wait_until_page_load(driver: uc.Chrome):
    WebDriverWait(driver, timeout=10).until_not(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'div[id="j_idt350_modal"]'
    )))


def wait_for_element(driver: uc.Chrome, by: str, locator: str, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))


def parse_html(driver: uc.Chrome, search_id: str) -> HTMLParser:
    URL = "https://supa.funcionjudicial.gob.ec/pensiones/publico/consulta.jsf"

    try:
        driver.get(URL)

        wait_for_element(
            driver, By.CSS_SELECTOR, 'input[id="form:t_texto_cedula"]').send_keys(search_id)

        driver.find_element(
            By.CSS_SELECTOR, 'button[id="form:b_buscar_cedula"]'
        ).send_keys(Keys.ENTER)

        wait_until_page_load(driver)

        try:
            driver.find_element(
                By.XPATH, '//td[contains(@role,"gridcell") and button]/button')
        except:
            raise Exception("Not Found D:")

        elements = driver.find_elements(
            By.CSS_SELECTOR, '.ui-datatable .ui-datatable-data>tr'
        )

        for record in elements:
            parse_table(driver, record)

    finally:
        driver.quit()

    return HTMLParser(str_html)


def parse_table(driver: uc.Chrome, element: WebElement):
    element.find_element(By.CSS_SELECTOR, ".ui-button.ui-widget").click()

    wait_until_page_load(driver)

    driver.find_element(
        By.CSS_SELECTOR, 'button[id="form:ta_co_movimientosPendientes"]'
    ).click()

    wait_until_page_load(driver)

    with open("parsed_html", "a") as file:
        file.write(driver.page_source)

    driver.find_element(
        By.CSS_SELECTOR, 'button[id="form:ta_co_cerrarPendientes"]'
    ).click()

    wait_until_page_load(driver)

    driver.find_element(
        By.CSS_SELECTOR, 'button[id="form:j_idt136"]'
    ).click()


def run():
    driver = setup_driver()
    parse_html(driver, "1709026718")


if __name__ == "__main__":
    run()

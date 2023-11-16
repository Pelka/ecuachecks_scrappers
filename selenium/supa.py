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
from typing import Generator
from dataclasses import dataclass, asdict

from pprint import pprint
from click import command, option
import crawlab


@dataclass
class SupaItem:
    province: str
    jurisdictional_depency: str
    card_code: str
    judicial_process: str
    type_alimony: str
    current_payment: str
    legal_representative: str
    primary_obligator: str
    n_pending_alimony: str
    subtotal_alimony_payments: str
    subtotal_alimony_interest: str
    total_alimony_payint: str
    n_other_debts: str
    total_other_debts: str


def setup_driver():
    # Configuraciones de undetected_chromedriver para evitar la detección
    USER_AGENT = UserAgent(os=["windows"], min_percentage=15.0).random

    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
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

    return driver


def wait_until_page_load(driver: uc.Chrome):
    WebDriverWait(driver, timeout=10).until_not(EC.presence_of_element_located((
        By.CSS_SELECTOR, 'div[id="j_idt350_modal"]'
    )))


def wait_for_element(driver: uc.Chrome, by: str, locator: str, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))


def get_html(driver: uc.Chrome, search_id: str) -> Generator[HTMLParser, any, None]:
    URL = "https://supa.funcionjudicial.gob.ec/pensiones/publico/consulta.jsf"

    try:
        driver.get(URL)

        wait_for_element(
            driver, By.CSS_SELECTOR, 'input[id="form:t_texto_cedula"]').send_keys(search_id)

        driver.find_element(
            By.CSS_SELECTOR, 'button[id="form:b_buscar_cedula"]'
        ).send_keys(Keys.ENTER)

        driver.implicitly_wait(5)
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
            yield HTMLParser(parse_table(driver, record))

    finally:
        driver.quit()


def parse_table(driver: uc.Chrome, element: WebElement):
    element.find_element(By.CSS_SELECTOR, ".ui-button.ui-widget").click()

    wait_until_page_load(driver)

    first_node = HTMLParser(driver.page_source)\
        .css_first('div[id="form:dDetalle"] tr')

    driver.find_element(
        By.CSS_SELECTOR, 'button[id="form:ta_co_movimientosPendientes"]'
    ).click()

    wait_until_page_load(driver)

    second_node = HTMLParser(driver.page_source)\
        .css_first('div[id="form:d_pendientes"]')

    driver.find_element(
        By.CSS_SELECTOR, 'button[id="form:ta_co_cerrarPendientes"]'
    ).click()

    wait_until_page_load(driver)

    driver.find_element(
        By.CSS_SELECTOR, 'button[id="form:j_idt136"]'
    ).click()

    html = first_node.html + second_node.html

    return html


def parse_data(html: Generator[HTMLParser, any, None]):
    for tree in html:
        general_data = tree.css('.tabla-columna-datos')
        table = tree.css_first('div[id="form:j_idt183"] + table')
        debts_data = table.css('td:nth-child(2), td:nth-child(5)')

        item = SupaItem(
            province=general_data[0].text(strip=True),
            jurisdictional_depency=general_data[1].text(strip=True),
            card_code=general_data[2].text(strip=True),
            judicial_process=general_data[3].text(strip=True),
            type_alimony=general_data[4].text(strip=True),
            current_payment=general_data[5].text(strip=True),
            legal_representative=general_data[6].text(strip=True),
            primary_obligator=general_data[8].text(strip=True),
            n_pending_alimony=debts_data[0].text(strip=True),
            subtotal_alimony_payments=debts_data[1].text(strip=True),
            subtotal_alimony_interest=debts_data[2].text(strip=True),
            total_alimony_payint=debts_data[3].text(strip=True),
            n_other_debts=debts_data[4].text(strip=True),
            total_other_debts=debts_data[7].text(strip=True)
        )

        pprint(asdict(item))

        crawlab.save_item(asdict(item))


def run(search_id: str):
    driver = setup_driver()
    html = get_html(driver, search_id)
    parse_data(html)


@command()
@option('--search_id', '-s', help="The id (cedula) to scrape")
def cli(search_id):
    # Search ID  # 1709026718 404:1721194593
    run(search_id)


cli()

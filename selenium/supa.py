# Selenium and related imports
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from seleniumwire.undetected_chromedriver import v2 as uc

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
import crawlab

PROXY_HTTP = "http://customer-ecuachecks-cc-ec:Ecuachecks2023@pr.oxylabs.io:7777"
PROXY_HTTPS = "https://customer-ecuachecks-cc-ec:Ecuachecks2023@pr.oxylabs.io:7777"
USER_AGENT = UserAgent(os=["windows"], min_percentage=15.0).random
URL = "https://supa.funcionjudicial.gob.ec/pensiones/publico/consulta.jsf"


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
    total: str


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
    options.add_argument(f'--user-agent={USER_AGENT}')

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
        version_main=106
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


def get_html(driver: uc.Chrome, search_id: str) -> Generator[HTMLParser, any, None]:

    try:
        driver.get(URL)

        driver.find_element(
            By.CSS_SELECTOR, 'input[id="form:t_texto_cedula"]'
        ).send_keys(search_id)

        driver.find_element(
            By.CSS_SELECTOR, 'button[id="form:b_buscar_cedula"]'
        ).send_keys(Keys.ENTER)

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//td[contains(@role,"gridcell") and button]/button')))
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
    wait = WebDriverWait(driver, 10)

    element.find_element(By.CSS_SELECTOR, ".ui-button.ui-widget").click()

    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'button[id="form:ta_co_movimientosPendientes"]'))
    ).click()

    c_btn = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'button[id="form:ta_co_cerrarPendientes"]')
    ))

    source = driver.page_source

    c_btn.click()

    wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, '.ui-dialog-footer.ui-widget-content span button:last-child')
    )).click()

    return source


def parse_data(parser: Generator[HTMLParser, any, None]):
    for tree in parser:
        general_data = tree.css(
            'div[id="form:dDetalle"] tr .tabla-columna-datos')
        table = tree.css_first(
            'div[id="form:d_pendientes"] .ui-dialog-content.ui-widget-content > table')

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
            total=debts_data[4].text(strip=True),
            n_other_debts=debts_data[5].text(strip=True),
            total_other_debts=debts_data[8].text(strip=True)
        )

        dict_item = asdict(item)
        crawlab.save_item(dict_item)
        pprint(dict_item)


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

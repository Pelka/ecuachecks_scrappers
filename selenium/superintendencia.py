# Selenium and related imports
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire.undetected_chromedriver import webdriver as uc

# Third-party libraries for enhanced web scraping
from selectolax.parser import HTMLParser
from fake_useragent import UserAgent
from selenium_stealth import stealth

# Data handling and utility tools
from dataclasses import dataclass, asdict, field, fields
from pprint import pprint

# CLI tools and custom modules
from click import command, option
import crawlab
import random

import time

PROXY_HTTP = "http://customer-ecuachecks-cc-ec-sessid-0620968049-sesstime-3:Ecuachecks2023@pr.oxylabs.io:7777"
PROXY_HTTPS = "https://customer-ecuachecks-cc-ec-sessid-0620968049-sesstime-3:Ecuachecks2023@pr.oxylabs.io:7777"
USER_AGENT = UserAgent(os=["windows"], min_percentage=15.0).random
URL = "https://appscvs1.supercias.gob.ec/consultaPersona/consulta_cia_personas.zul"


@dataclass
class AdministrationItem:
    id_file: str
    name: str
    ruc: str
    nationality: str
    position: str
    appointment_date: str
    end_date: str
    period: str
    com_reg_date: str
    article: str
    com_reg_number: str
    lr_a: str


@dataclass
class ShareholderItem:
    id_file: str
    name: str
    ruc: str
    invested_capital: str
    total_company_capital: str
    nominal_value: str
    legal_status: str
    effective_possession: str


@dataclass
class superintendenciaItem:
    current_administration: list[AdministrationItem] = field(default_factory=list)
    current_shareholder: list[ShareholderItem] = field(default_factory=list)


def setup_driver():
    # Settings of undetected_chromedriver to avoid detection
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
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
        seleniumwire_options=wire_options,
        # version_main=106,
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


def get_html(driver: uc.Chrome, search_id: str):
    try:
        driver.get(URL)

        param_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//span[contains(text(), 'Parametro:')]/following-sibling::i[contains(@class, 'z-combobox')]/input",
                )
            )
        )

        param_input.click()

        for letter in search_id:
            param_input.send_keys(letter)
            time.sleep(random.randint(50, 200) / 1000)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//td[@class='z-comboitem-text']"))
        )

        param_input.send_keys(Keys.TAB)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table[@style='table-layout:fixed;']")
            )
        )

        return HTMLParser(driver.page_source)
    finally:
        driver.quit()


def create_item(data: list[any], item_class: dataclass):
    field_names = [field.name for field in fields(item_class)]
    if len(data) >= len(field_names):
        dic_data = {
            field_names[i]: data[i].text(strip=True) for i in range(len(field_names))
        }
        item = item_class(**dic_data)
    else:
        raise Exception("Mismatch between data length and expected fields")

    return item


def parse_data(parser: HTMLParser):  # parser: HTMLParser
    tables = parser.css(".z-groupbox-3d")

    item = superintendenciaItem()

    for i in range(2):
        rows = tables[i].css_first("div.z-listbox-body tbody:nth-child(2)").css("tr")
        for row in rows:
            data = row.css("td")

            if i == 0:
                subitem = create_item(data, AdministrationItem)
                item.current_administration.append(subitem)
            else:
                # field_names = [field.name for field in fields(ShareholderItem)]
                # dic_data = {field_names[i]: data[i].text(strip=True) for i in range(8)}
                # subitem = ShareholderItem(**dic_data)
                subitem = create_item(data, ShareholderItem)
                item.current_shareholder.append(subitem)

    dic_item = asdict(item)
    crawlab.save_item(dic_item)
    pprint(dic_item)


def run(search_id: str):
    driver = setup_driver()
    data = get_html(driver, search_id)
    parse_data(data)


@command()
@option("--search_id", "-s", help="The id (cedula) to scrape")
def cli(search_id):
    # 1721194593 1725514119 1721194592 1709026718 0922485172
    run(search_id)


cli()

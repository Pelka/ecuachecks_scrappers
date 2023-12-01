# Selenium and related imports
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire.undetected_chromedriver import webdriver as uc

# Third-party libraries for enhanced web scraping
from selectolax.parser import HTMLParser
from fake_useragent import UserAgent
from selenium_stealth import stealth

# Data handling and utility tools
from dataclasses import dataclass, asdict, field
from pprint import pprint

# CLI tools and custom modules
from click import command, option
import crawlab

import time


PROXY_HTTP = "http://customer-ecuachecks-cc-ec-sessid-0620968049-sesstime-3:Ecuachecks2023@pr.oxylabs.io:7777"
PROXY_HTTPS = "https://customer-ecuachecks-cc-ec-sessid-0620968049-sesstime-3:Ecuachecks2023@pr.oxylabs.io:7777"
USER_AGENT = UserAgent(os=["windows"], min_percentage=15.0).random
URL = (
    "https://www.gestiondefiscalias.gob.ec/siaf/informacion/web/noticiasdelito/index.php"
)


@dataclass
class PersonItem:
    id_number: str
    full_name: str
    status: str


@dataclass
class FisGenEstadoItem:
    no_process: str
    place: str
    date: str
    state: str
    no_office: str
    crime: str
    unit: str
    attorney: str
    people: list[PersonItem] = field(default_factory=list)


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
        version_main=106,
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

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pwd"))
        ).send_keys(search_id)

        driver.find_elements(By.ID, "buscar")[2].click()

        time.sleep(3)

        return HTMLParser(driver.page_source)
    finally:
        driver.quit()


def parse_data(parser: HTMLParser):
    node = parser.css_first("div#resultados")
    trees = node.css(".general")

    for tree in trees:
        tables = tree.css("table")

        crime_table = tables[0]
        people_table = tables[1]

        crime_data = crime_table.css("td")
        people_data = people_table.css("tbody tr")

        item = FisGenEstadoItem(
            no_process=crime_table.css_first("th").text().split(".")[1].strip(),
            place=crime_data[2].text(),
            date=f"{crime_data[4].text()} {crime_data[6].text()}",
            state=crime_data[10].text(),
            no_office=crime_data[12].text(),
            crime=crime_data[14].text(),
            unit=crime_data[16].text(),
            attorney=crime_data[17].text(),
        )

        for person in people_data:
            data = person.css("td")
            subitem = PersonItem(
                id_number=data[0].text(strip=True),
                full_name=data[1].text(strip=True),
                status=data[2].text(strip=True),
            )
            item.people.append(subitem)

        dict_item = asdict(item)
        crawlab.save_item(dict_item)
        pprint(dict_item)


def run(search_id: str):
    driver = setup_driver()
    data = get_html(driver, search_id)
    parse_data(data)


@command()
@option("--search_id", "-s", help="The id (cedula) to scrape")
def cli(search_id):
    # 1309022935
    run(search_id)


cli()

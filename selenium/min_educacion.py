# Selenium and related imports
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Third-party libraries for enhanced web scraping
from selectolax.parser import HTMLParser
from fake_useragent import UserAgent
from selenium_stealth import stealth
from twocaptcha import TwoCaptcha

# Data handling and utility tools
from dataclasses import dataclass, asdict
from pprint import pprint

# CLI tools and custom modules
from click import command, option
import crawlab

TWO_CAPTCHA_API_KEY = "331b57cff358c0e42f3529ab52c8409b"
USER_AGENT = UserAgent(os=["windows"], min_percentage=15.0).random
PROXY = "https://customer-ecuachecks-cc-ec:Ecuachecks2023@pr.oxylabs.io:7777"
URL = "https://servicios.educacion.gob.ec/titulacion25-web/faces/paginas/consulta-titulos-refrendados.xhtml"


@dataclass
class MinEducacionItem:
    no: str
    id_number: str
    full_name: str
    college: str
    degree: str
    speciality: str
    graduation_date: str
    ref_number: str


def setup_driver():
    # Settings of undetected_chromedriver to avoid detection
    options = webdriver.ChromeOptions()
    service = Service(ChromeDriverManager().install())

    options.add_argument('--headless=new')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-plugins-discovery')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--incognito')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f'user-agent={USER_AGENT}')

    wire_options = {
        'connection_timeout': None,  # Wait forever for the connection to start
        'connection_keep_alive': True,  # Use connection keep-alive
        'proxy': {
            'https': PROXY
        },
    }

    # Setup driver
    driver = webdriver.Chrome(
        options=options,
        service=service,
        seleniumwire_options=wire_options,
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


def captcha_solver(img_src):
    solver = TwoCaptcha(TWO_CAPTCHA_API_KEY)
    result = {}

    try:
        result = solver.normal(
            img_src,
            phrase=False,
            caseSensitive=True,
            minLen=6,
            maxLen=6
        )

        result = solver.normal(
            img_src,
            hintText=result.get('code'),
            minLen=6,
            maxLen=6
        )

        print("Response:", result)
    except Exception as e:
        raise e

    return result


def wait_until_page_load(driver: webdriver.Chrome, timeout=5):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(
            'return document.readyState') == 'complete'
    )


def get_html(driver: webdriver.Chrome, search_id: str):

    try:
        driver.get(URL)

        wait_until_page_load(driver)

        img_b64 = driver.find_element(
            By.CSS_SELECTOR, 'img[id="formBusqueda:capimg"]'
        ).screenshot_as_base64

        result = captcha_solver(img_b64)

        driver.find_element(
            By.CSS_SELECTOR, 'input[id="formBusqueda:cedula"]'
        ).send_keys(search_id)

        driver.find_element(
            By.CSS_SELECTOR, 'input[id="formBusqueda:captcha"]'
        ).send_keys(result.get('code'))

        driver.find_element(
            By.CSS_SELECTOR, 'input[id="formBusqueda:clBuscar"]'
        ).send_keys(Keys.ENTER)

        wait_until_page_load(driver)

        # TODO: make screenshot pipeline
        # driver.save_screenshot("output.png")

        return HTMLParser(driver.page_source)

    finally:
        driver.quit()


def parse_data(parser: HTMLParser):
    table_data = parser.css(
        'span[id="formBusqueda:tabla"] tbody.rf-dt-b tr')

    if table_data:
        for row in table_data:
            data = row.css("td.rf-dt-c")
            item = MinEducacionItem(
                no=data[0].text(strip=True),
                id_number=data[1].text(strip=True),
                full_name=data[2].text(strip=True),
                college=data[3].text(strip=True),
                degree=data[4].text(strip=True),
                speciality=data[5].text(strip=True),
                graduation_date=data[6].text(strip=True),
                ref_number=data[7].text(strip=True),
            )

            dict_item = asdict(item)
            crawlab.save_item(dict_item)
            pprint(dict_item)
    else:
        raise Exception("Not Found D:")


def run(search_id: str):
    driver = setup_driver()
    html = get_html(driver, search_id)
    parse_data(html)


@command()
@option('--search_id', '-s', help="The id (cedula) to scrape")
def cli(search_id):
    # 1721194593 1725514119 1721194592 1709026718 0922485172
    run(search_id)


cli()

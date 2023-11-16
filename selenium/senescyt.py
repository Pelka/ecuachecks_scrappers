# Selenium and related imports
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc

# Third-party libraries for enhanced web scraping
from selectolax.parser import HTMLParser, Node
from fake_useragent import UserAgent
from selenium_stealth import stealth
from twocaptcha import TwoCaptcha

# Data handling and utility tools
from dataclasses import dataclass, asdict, field
from pprint import pprint

# CLI tools and custom modules
from click import command, option
import crawlab


@dataclass
class DegreeItem:
    title: str
    college: str
    type: str
    recognized: str
    register_num: str
    register_date: str
    area: str
    note: str


@dataclass
class SenescytItem:
    id_number: str
    full_name: str
    gender: str
    nacionality: str
    degress: list[DegreeItem] = field(default_factory=list)


PROXY_HTTP = "http://customer-ecuachecks-cc-ec-sessid-0519303614-sesstime-5:Ecuachecks2023@pr.oxylabs.io:7777"
PROXY_HTTPS = "https://customer-ecuachecks-cc-ec-sessid-0519303614-sesstime-5:Ecuachecks2023@pr.oxylabs.io:7777"


def setup_driver():
    # Settings of undetected_chromedriver to avoid detection
    USER_AGENT = UserAgent(os=["windows"], min_percentage=15.0).random

    options = uc.ChromeOptions()
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
    options.set_capability("acceptInsecureCerts", True)
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


def captcha_solver(img_src):
    solver = TwoCaptcha("331b57cff358c0e42f3529ab52c8409b")
    result = {}

    try:
        result = solver.normal(img_src, proxy={
            'type': 'HTTP',
            'uri': PROXY_HTTP
        })
        print("Response:", result)
    except Exception as e:
        raise e

    return result


def wait_until_page_load(driver: uc.Chrome, timeout=10.0):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script(
            'return document.readyState') == 'complete'
    )


def wait_for_element(driver: uc.Chrome, by: str, locator: str, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))


def error_handler(tree: HTMLParser):
    try:
        e_msg = tree.css_first('.msg-rojo').text(strip=True)
    except:
        e_msg = tree.css_first('.ui-messages-error').text()

    raise Exception(e_msg)


def get_html(driver: uc.Chrome, search_id: str):
    URL = "http://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml;jsessionid=Fa3JjYFGiorrF4sr7TZQvZEKkMCJeLLQfYKjq8lS.srvprouioct26"

    try:
        driver.get(URL)

        wait_until_page_load(driver)

        img = driver.find_element(
            By.CSS_SELECTOR, 'img[id="formPrincipal:capimg"]'
        ).get_attribute("src")

        result = captcha_solver(img)

        if not result.get('code', ''):
            raise Exception("Failed captcha")

        driver.find_element(
            By.CSS_SELECTOR, 'input[id="formPrincipal:identificacion"]'
        ).send_keys(search_id)

        driver.find_element(
            By.CSS_SELECTOR, 'input[id="formPrincipal:captchaSellerInput"]'
        ).send_keys(result.get('code'))

        driver.find_element(
            By.CSS_SELECTOR, 'button[id="formPrincipal:boton-buscar"]'
        ).send_keys(Keys.ENTER)

        wait_until_page_load(driver)

        tree = HTMLParser(driver.page_source)

        try:
            driver.find_element(
                By.XPATH, '//div[contains(@id,"pnlListaTitulos") and contains(@class,"panel")]')
        except:
            error_handler(tree)

        return tree

    finally:
        driver.quit()


def parse_data(tree: HTMLParser):
    def get_text_safe(element: Node | None):
        return element.next.text() if element and element.next else ''

    personal_data = tree.css(
        'div#formPrincipal_pnlInfoPersonalcontent td.ui-panelgrid-cell.grid-left label')

    item = SenescytItem(
        id_number=personal_data[0].text(),
        full_name=personal_data[1].text(),
        gender=personal_data[2].text(),
        nacionality=personal_data[3].text(),
    )

    degrees_tree = tree.css('div[id*="pnlListaTitulos"][class*="panel"]')

    if degrees_tree:
        for panel in degrees_tree:
            degree_raw = panel.css_first('tbody')
            degree_data = degree_raw.css('td span')

            sub_item = DegreeItem(
                title=get_text_safe(degree_data[0]),
                college=get_text_safe(degree_data[1]),
                type=get_text_safe(degree_data[2]),
                recognized=get_text_safe(degree_data[3]),
                register_num=get_text_safe(degree_data[4]),
                register_date=get_text_safe(degree_data[5]),
                area=get_text_safe(degree_data[6]),
                note=get_text_safe(degree_data[7]),
            )

            item.degress.append(sub_item)

    pprint(asdict(item))
    crawlab.save_item(asdict(item))


def run(search_id: str):
    driver = setup_driver()
    html = get_html(driver, search_id)
    parse_data(html)


@command()
@option('--search_id', '-s', help="The id (cedula) to scrape")
def cli(search_id):
    run(search_id)


cli()

# if __name__ == "__main__":
#     # 1721194593 1709026718 1709822207
#     run("1709822207")

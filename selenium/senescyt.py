# develop library
from pprint import pprint

# Data processing
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, Field
from crawlab import save_item

# Selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Utils for webscraping
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions
from twocaptcha import TwoCaptcha

# Html parser
from selectolax.parser import HTMLParser, Node

# CLI commands
from click import command, option


# Data handlers
class PPDModel(BaseModel):
    """
    The PPDModel class provides common data cleaning operations for all fields string fields.

    Methods:
        strip_strings(v: Any): Strips whitespace from string values for all fields.
        capitalize_words(v: Optional[str]): Capitalizes the first letter of each word in string values for all fields.
    """

    @field_validator('*')
    @classmethod
    def strip_strings(cls, value: any) -> any:
        """
        Strips whitespace from string if `value` is a string, otherwise returns `value` unchanged.
        """
        return value.strip() if isinstance(value, str) else value

    @classmethod
    def capitalize_words(cls, value: str) -> str:
        """
        Capitalizes the first letter of each word in a string if `value` is a string.
        """
        words = value.split()
        capitalized_words = [word.capitalize() if len(
            word) > 1 else word for word in words]
        return ' '.join(capitalized_words)

    @classmethod
    def string_to_datetime(cls, value: str, date_format: str) -> datetime:
        """
        Converts a string to a datetime object according to the specified format.
        """
        return datetime.strptime(value, date_format)


class Degree(PPDModel):
    title: str
    college: Optional[str]
    certificate_type: Optional[str]
    recognized: Optional[str]
    register_num: Optional[str]
    register_date: datetime
    area: Optional[str]
    note: Optional[str]

    @field_validator('title', 'college', 'area', 'recognized', 'note')
    @classmethod
    def capitalize_words(cls, value: str) -> str:
        return super().capitalize_words(value)

    @field_validator('register_date', mode="before")
    @classmethod
    def string_to_datetime(cls, value: str) -> datetime:
        return super().string_to_datetime(value, "%Y-%m-%d")


class EducationProfile(PPDModel):
    id_number: str
    full_name: str
    gender: str
    nacionality: str
    degress: list[Degree] = Field(default_factory=list)

    @field_validator('gender', 'nacionality')
    def capitalize_words(cls, V: str):
        return super().capitalize_words(V)


class SenescytSpider:
    def __init__(self, search_id: str):
        # Test id: 1721194593 1709026718 1709822207
        self.search_id = search_id
        self.target_url = "https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml;jsessionid=Fa3JjYFGiorrF4sr7TZQvZEKkMCJeLLQfYKjq8lS.srvprouioct26"
        self.driver = self._setup_driver()

    @classmethod
    def start_from_cli(cls, search_id: str):
        spider = cls(search_id)
        status, data = spider.get_html()

        if status == "Ok":
            item = spider.parse_data(data)
            save_item(item.model_dump(mode='json'))
            pprint(item.model_dump())
        else:
            spider.parse_error(data)

    def _setup_driver(self):
        # Setting Chrome options
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-dev-shm-usage')

        # Fake user agent
        ua = UserAgent().random
        options.add_argument(f"--user-agent={ua}")

        # Setting up ChromeDriver
        service = Service(
            executable_path=ChromeDriverManager().install()
        )

        driver = uc.Chrome(
            service=service,
            use_subprocess=False,
            options=options,
            # version_main=106
        )

        # Setting implitly wait time
        driver.implicitly_wait(10)
        return driver

    def _captcha_solver(self, img_src):
        solver = TwoCaptcha("331b57cff358c0e42f3529ab52c8409b")
        result = {}

        try:
            result = solver.normal(img_src)
            print("Response:", result)
        except Exception as e:
            raise e

        return result

    def _wait_for_page_load(self, timeout: int = 10):
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script(
                'return document.readyState') == 'complete'
        )

    def get_html(self):
        self.driver.get(self.target_url)

        self._wait_for_page_load()

        img = self.driver.find_element(
            By.CSS_SELECTOR, 'img[id="formPrincipal:capimg"]'
        ).get_attribute("src")

        result = self._captcha_solver(img)

        if not result.get('code', ''):
            raise Exception("Failed captcha")

        self.driver.find_element(
            By.CSS_SELECTOR, 'input[id="formPrincipal:identificacion"]'
        ).send_keys(self.search_id)

        self.driver.find_element(
            By.CSS_SELECTOR, 'input[id="formPrincipal:captchaSellerInput"]'
        ).send_keys(result.get('code'))

        self.driver.find_element(
            By.CSS_SELECTOR, 'button[id="formPrincipal:boton-buscar"]'
        ).send_keys(Keys.ENTER)

        self._wait_for_page_load()

        try:
            self.driver.find_element(
                By.XPATH, '//div[contains(@id,"pnlListaTitulos") and contains(@class,"panel")]')
        except:
            resp_msg = "Error"
        else:
            resp_msg = "Ok"

        resp_data = HTMLParser(self.driver.page_source)
        self.driver.quit()

        return (resp_msg, resp_data)

    def parse_error(self, tree: HTMLParser):
        try:
            err_msg = tree.css_first('.msg-rojo').text()
        except:
            err_msg = tree.css_first('.ui-messages-error').text()
        raise Exception(err_msg)

    def parse_data(self, tree: HTMLParser):

        def get_text_safe(element: Node | None):
            return element.next.text() if element and element.next else ''

        personal_data = tree.css(
            'div#formPrincipal_pnlInfoPersonalcontent td.ui-panelgrid-cell.grid-left label')

        item = EducationProfile(
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

                sub_item = Degree(
                    title=get_text_safe(degree_data[0]),
                    college=get_text_safe(degree_data[1]),
                    certificate_type=get_text_safe(degree_data[2]),
                    recognized=get_text_safe(degree_data[3]),
                    register_num=get_text_safe(degree_data[4]),
                    register_date=get_text_safe(degree_data[5]),
                    area=get_text_safe(degree_data[6]),
                    note=get_text_safe(degree_data[7]),
                )

                item.degress.append(sub_item)

        return item


@command()
@option('--search_id', '-s', help="The id (cedula) to scrape")
def cli(search_id):
    SenescytSpider.start_from_cli(search_id)


cli()

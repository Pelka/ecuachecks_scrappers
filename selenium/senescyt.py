from typing import Optional
from pydantic import BaseModel, field_validator, Field

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from fake_useragent import UserAgent
import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions

from selectolax.parser import HTMLParser, Node
from twocaptcha import TwoCaptcha


class Degree(BaseModel):
    title: str
    college: Optional[str]
    certificate_type: Optional[str]
    recognized: Optional[str]
    register_num: Optional[str]
    register_date: Optional[str]
    area: Optional[str]
    note: Optional[str]

    @field_validator('*')
    @classmethod
    def strip_strings(cls, V: any) -> str:
        return V.strip() if isinstance(V, str) else V

    @field_validator('title', 'college', 'area', 'recognized', 'note')
    @classmethod
    def capitalize_words(cls, V: str | None):
        if V is not None:
            words = V.split()
            capitalized_words = [
                word.capitalize() if len(word) > 1 else word for word in words
            ]
            V = ' '.join(capitalized_words)
            return V
        else:
            return V


class EducationProfile(BaseModel):
    id_number: str
    full_name: str
    gender: str
    nacionality: str
    degress: list[Degree] = Field(default_factory=list)

    @field_validator('*')
    @classmethod
    def strip_strings(cls, V: any) -> str:
        return V.strip() if isinstance(V, str) else V

    @field_validator('gender', 'nacionality')
    @classmethod
    def capitalize_words(cls, V: str):
        if V is not None:
            words = V.split()
            capitalized_words = [
                word.capitalize() if len(word) > 1 else word for word in words
            ]
            V = ' '.join(capitalized_words)
            return V
        else:
            return V


class SenescytSpider:
    def __init__(self, search_id: str):
        self.search_id = search_id
        self.target_url = "https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml;jsessionid=Fa3JjYFGiorrF4sr7TZQvZEKkMCJeLLQfYKjq8lS.srvprouioct26"
        self.options = self._set_chrome_arguments([
            "--headless",
            "--disable-gpu",
            f"--user-agent='{UserAgent().chrome}'",
        ])
        self.driver = self._init_driver(self.options)
        self.driver.implicitly_wait(10)

    def _set_chrome_arguments(self, arguments):
        chrome_options = ChromeOptions()
        for argument in arguments:
            chrome_options.add_argument(argument)
        return chrome_options

    def _init_driver(self, options):
        service = Service()
        return uc.Chrome(
            service=service,
            use_subprocess=True,
            options=options
        )

    def _captcha_solver(self, img_src):
        solver = TwoCaptcha("331b57cff358c0e42f3529ab52c8409b")
        result = {}

        try:
            result = solver.normal(img_src)
            print("Response:", result)
        except Exception as e:
            raise e

        return result

    def _wait_for_element(self, selector, timeout=10, by=By.CSS_SELECTOR):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )

    def get_html(self):
        self.driver.get(self.target_url)

        img = self._wait_for_element(
            'img[id="formPrincipal:capimg"]').get_attribute("src")

        result = self._captcha_solver(img)

        try:
            if result.get('code', ''):
                self._wait_for_element(
                    'input[id="formPrincipal:identificacion"]'
                ).send_keys(self.search_id)

                self._wait_for_element(
                    'input[id="formPrincipal:captchaSellerInput"]'
                ).send_keys(result.get("code"))

                self.driver.find_element(
                    By.CSS_SELECTOR, 'button[id="formPrincipal:boton-buscar"]'
                ).send_keys(Keys.ENTER)

                try:
                    self._wait_for_element('formPrincipal:j_idt39', 20, By.ID)
                except:
                    resp_msg = "Error"
                else:
                    resp_msg = "Ok"

                resp_data = HTMLParser(self.driver.page_source)

                return (resp_msg, resp_data)
            else:
                raise Exception("Failed captcha")

        except:
            raise Exception("Couldn't interact with the page")

        finally:
            self.driver.quit()

    def parse_error(self, tree: HTMLParser):
        err_msg = tree.css_first('.msg-rojo').text().strip()
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


if __name__ == "__main__":
    spider = SenescytSpider(search_id="1721194593")
    status, data = spider.get_html()

    if status == "Ok":
        item = spider.parse_data(data)
    else:
        item = spider.parse_error(data)

    print(item)

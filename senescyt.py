import time
from scrapy import Spider, Request, Selector
import chromedriver_autoinstaller
import undetected_chromedriver as uc
from scrapy import Request, Spider
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twocaptcha import TwoCaptcha
import sys
import os
from undetected_chromedriver import Chrome, ChromeOptions


class senescytSpider(Spider):
    name = "senescyt"
    start_urls = ['https://quotes.toscrape.com/']
    url = "https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml;jsessionid=Fa3JjYFGiorrF4sr7TZQvZEKkMCJeLLQfYKjq8lS.srvprouioct26"

    def parse(self, response, **kwargs):
        user_input = input("Enter ID: ")  # 1721194593 1709026718
        # user_input = '1709822207'
        options = ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = uc.Chrome(
            executable_path=chromedriver_autoinstaller.install(),
            chrome_options=options,
        )
        driver.get(self.url)
        time.sleep(10)

        img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'img[id="formPrincipal:capimg"]'))
        ).get_attribute('src')
        sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        api_key = os.getenv('APIKEY_2CAPTCHA', '331b57cff358c0e42f3529ab52c8409b')
        solver = TwoCaptcha(api_key)
        result = {}
        try:
            result = solver.normal(
                img
            )
            print("Response:", result)
        except Exception as e:
            print("Error:", str(e))

        if result.get('code', ''):
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[id="formPrincipal:identificacion"]'))
            ).send_keys(user_input)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[id="formPrincipal:captchaSellerInput"]'))
            ).send_keys(result.get('code'))
            driver.find_element(By.CSS_SELECTOR, 'button[id="formPrincipal:boton-buscar"]').send_keys(Keys.ENTER)
            driver.implicitly_wait(10)
            response = driver.page_source
            time.sleep(10)
            data = Selector(text=response)
            time.sleep(10)
            if data.xpath('//div[contains(@id,"pnlListaTitulos") and contains(@class,"panel")]'):
                for record in data.xpath('//div[contains(@id,"pnlListaTitulos") and contains(@class,"panel")]'):
                    table_data = record.css('tbody')
                    records = data.css('#formPrincipal_pnlInfoPersonalcontent tbody')[0]
                    res = {
                        'ID Number': records.xpath(
                            './/td[label[contains(text(),"Identificación")]]/following-sibling::td/label/text()').get(
                            ''),
                        'Full name': records.xpath(
                            './/td[label[contains(text(),"Nombres")]]/following-sibling::td/label/text()').get(''),
                        'Gender': records.xpath(
                            './/td[label[contains(text(),"Género")]]/following-sibling::td/label/text()').get(''),
                        'Nationality': records.xpath(
                            './/td[label[contains(text(),"Nacionalidad")]]/following-sibling::td/label/text()').get(''),
                        'Degree': table_data.xpath('.//td[span[contains(text(),"Título")]]/text()').get(''),
                        'College': table_data.xpath(
                            './/td[span[contains(text(),"Institución de Educación Superior")]]/text()').get(''),
                        'Type': table_data.xpath('.//td[span[contains(text(),"Tipo")]]/text()').get(''),
                        'Recognized by': table_data.xpath('.//td[span[contains(text(),"Reconocido Por")]]/text()').get(
                            ''),
                        'Register Number': table_data.xpath(
                            './/td[span[contains(text(),"Número de Registro")]]/text()').get(''),
                        'Date of register': table_data.xpath(
                            './/td[span[contains(text(),"Fecha de Registro")]]/text()').get(''),
                        'Area': table_data.xpath(
                            './/td[span[contains(text(),"Área o Campo de Conocimiento")]]/text()').get(
                            ''),
                        'Note': table_data.xpath('.//td[span[contains(text(),"Observación")]]/text()').get(''),
                    }
                    yield res
            else:
                res = {
                    'Message': data.css('.msg-rojo::text').get('').strip()
                }
                yield res

            driver.close()

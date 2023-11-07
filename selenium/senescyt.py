import time
from pprint import pprint
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from undetected_chromedriver import ChromeOptions
from twocaptcha import TwoCaptcha

# --- Init config
# user_input = input("Enter ID: ")  # 1721194593 1709026718
search_id = '1709822207'
url = 'https://www.senescyt.gob.ec/consulta-titulos-web/faces/vista/consulta/consulta.xhtml;jsessionid=Fa3JjYFGiorrF4sr7TZQvZEKkMCJeLLQfYKjq8lS.srvprouioct26'

options = ChromeOptions()
service = Service()

# options.add_argument('--headless')
# options.add_argument('--disable-gpu')

driver = webdriver.Chrome(
    service=service,
    # use_subprocess=True,
    # options=options,
)

driver.get(url)

wait = WebDriverWait(driver, timeout=10)

img = wait.until(
    EC.presence_of_element_located(
        (By.CSS_SELECTOR, 'img[id="formPrincipal:capimg"]')
    )
).get_attribute("src")

solver = TwoCaptcha("331b57cff358c0e42f3529ab52c8409b")

result = {}

try:
    result = solver.normal(img)
    print("Response: ", result)
except Exception as e:
    print("Error:", str(e))

if result.get("code", ""):
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[id="formPrincipal:identificacion"]')
        )
    ).send_keys(search_id)

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[id="formPrincipal:captchaSellerInput"]')
        )
    ).send_keys(result.get("code"))

    driver.find_element(
        By.CSS_SELECTOR, 'button[id="formPrincipal:boton-buscar"]'
    ).send_keys(Keys.ENTER)

    driver.implicitly_wait(7)

    response = driver.page_source

    driver.implicitly_wait(7)

    data = html.fromstring(response)

    titles = data.xpath(
        '//div[contains(@id,"pnlListaTitulos") and contains(@class,"panel")]')

    if titles:
        for record in titles:
            table_data = record.xpath('.//tbody')[0]
            records = table_data.xpath(
                './/*[@id="formPrincipal_pnlInfoPersonalcontent"]//tbody')

            print(html.tostring(records, pretty_print=True).decode("utf-8"))

            # print(html.tostring(records.xpath(
            #     './/td[label[contains(., "Nombres:")]]/following-sibling::td/label/text()')))

            # senescyt_item = {}

            # senescyt_item["full_name"] = records.xpath(
            #     '//td[label[contains(., "Nombres:")]]/following-sibling::td/label/text()')[0].text
            # senescyt_item["cedula"] = records.xpath(
            #     './/td[label[contains(text(),"Identificación")]]/following-sibling::td/label/text()').get("")
            # senescyt_item["gender"] = records.xpath(
            #     './/td[label[contains(text(),"Género")]]/following-sibling::td/label/text()').get("")
            # senescyt_item["nationality"] = records.xpath(
            #     './/td[label[contains(text(),"Nacionalidad")]]/following-sibling::td/label/text()').get("")
            # senescyt_item["degree"] = table_data.xpath(
            #     './/td[span[contains(text(),"Título")]]/text()').get("")
            # senescyt_item["college"] = table_data.xpath(
            #     './/td[span[contains(text(),"Institución de Educación Superior")]]/text()').get("")
            # senescyt_item["certificate_type"] = table_data.xpath(
            #     './/td[span[contains(text(),"Tipo")]]/text()').get("")
            # senescyt_item["recognized"] = table_data.xpath(
            #     './/td[span[contains(text(),"Reconocido Por")]]/text()').get("")
            # senescyt_item["register_number"] = table_data.xpath(
            #     './/td[span[contains(text(),"Número de Registro")]]/text()').get("")
            # senescyt_item["register_date"] = table_data.xpath(
            #     './/td[span[contains(text(),"Fecha de Registro")]]/text()').get("")
            # senescyt_item["area"] = table_data.xpath(
            #     './/td[span[contains(text(),"Área o Campo de Conocimiento")]]/text()').get("")
            # senescyt_item["note"] = table_data.xpath(
            #     './/td[span[contains(text(),"Observación")]]/text()').get("")

            # pprint(senescyt_item)

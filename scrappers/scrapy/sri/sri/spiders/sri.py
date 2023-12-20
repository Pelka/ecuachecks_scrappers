from copy import deepcopy
from scrapy import Spider, Request
from twocaptcha import TwoCaptcha
from scrapy.exceptions import CloseSpider

from sri.items import SriItem


class SriSpider(Spider):
    handle_httpstatus_list = [400]
    name = "sri"
    url = "https://srienlinea.sri.gob.ec/sri-registro-civil-servicio-internet/rest/DatosRegistroCivil/obtenerDatosCompletosPorNumeroIdentificacionConToken?numeroIdentificacion={}"

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS": 10,
    }

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Connection": "keep-alive",
        "Content-Type": "application/json; charset=utf-8",
        # 'Expires': 'Sat, 01 Jan 2000 00:00:00 GMT',
        "If-Modified-Since": "0",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Cookie": "BIGipServerDecla_Sesion=119406858.47873.0000; TS01ed1cee=0115ac86d2cabfc21cc7363a9ec57e688b292a215099bf5e1a451cfee58ebce50e196b0b0f36922fdda2cf956a633e719afa500c3a99a4ca41ac5ac01008cf90794c01bc1e",
    }

    def __init__(self, search_id: str, **kwargs):
        super().__init__(**kwargs)
        url = "https://srienlinea.sri.gob.ec/sri-en-linea/SriPagosWeb/ConsultaDeudasFirmesImpugnadas/Consultas/consultaDeudasFirmesImpugnadas"
        site_key = "6Lc6rokUAAAAAJBG2M1ZM1LIgJ85DwbSNNjYoLDk"
        solver = TwoCaptcha("331b57cff358c0e42f3529ab52c8409b")
        self.search_id = search_id

        try:
            result = solver.recaptcha(sitekey=site_key, url=url)
            print("Response:", result)
            self.code = result.get("code")
        except Exception as e:
            print("Error:", str(e))

    def start_requests(self):
        detail_url = "https://srienlinea.sri.gob.ec/sri-captcha-servicio-internet/rest/ValidacionCaptcha/validarGoogleReCaptcha?googleCaptchaResponse={}&emitirToken=true"
        yield Request(detail_url.format(self.code), callback=self.get_token, headers=self.headers)

    def get_token(self, response):
        data = response.json()
        headers = deepcopy(self.headers)
        headers["Authorization"] = data.get("mensaje")
        url = "https://srienlinea.sri.gob.ec/sri-registro-civil-servicio-internet/rest/DatosRegistroCivil/obtenerDatosCompletosPorNumeroIdentificacionConToken?numeroIdentificacion={}"
        yield Request(
            url.format(self.search_id),
            callback=self.parse,
            headers=headers,
            meta={"headers": headers},
        )

    def parse(self, response, **kwargs):
        if response.status == 204:
            url = "https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/Persona/obtenerPersonaDesdeRucPorIdentificacion?numeroRuc={}"
            yield Request(
                url.format(self.search_id),
                callback=self.parse,
                headers=response.meta["headers"],
                meta=response.meta,
            )
        elif response.status == 400:
            raise CloseSpider("Not Found Data")
        else:
            data = response.json()

            sri_item = SriItem()

            sri_item["full_name"] = data.get("nombreCompleto", "")
            sri_item["id_number"] = data.get("identificacion", "")
            sri_item["message"] = ""
            sri_item["firm_debts"] = "0"
            sri_item["disputed_debts"] = "0"
            sri_item["payment_facilities"] = "0"

            url = "https://srienlinea.sri.gob.ec/sri-deudas-servicio-internet/rest/ConsultaDeuda/obtenerDeudaPorIdentificacion?identificacion={}"
            yield Request(
                url.format(self.search_id),
                callback=self.response_data,
                headers=response.meta["headers"],
                meta={"item": sri_item},
            )

    def response_data(self, response):
        data = response.json()
        sri_item = response.meta["item"]
        if data.get("suspendidas", ""):
            if "deudaFirme" in list(data.keys()):
                sri_item["firm_debts"] = f"${data.get('deudaFirme', '')}"
            if "suspendidas" in list(data.keys()):
                sri_item["disputed_debts"] = f"${data.get('suspendidas', '')}"
            if "oficinaCobranzas" in list(data.keys()):
                sri_item["payment_facilities"] = data.get("oficinaCobranzas", "")
                if sri_item["payment_facilities"] is None:
                    sri_item["payment_facilities"] = "0.0"

        else:
            sri_item[
                "message"
            ] = "El ciudadano / contribuyente no registra deudas firmes, impugnadas o en facilidades de pago."

        yield sri_item

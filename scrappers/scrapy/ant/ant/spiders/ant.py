from ant.items import AntItem, NotFoundItem

from scrapy import Request, Spider


class AntSpider(Spider):
    name = "ant"
    allowed_domains = ["consultaweb.ant.gob.ec"]
    start_urls = [
        "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_grid_citaciones.jsp?ps_tipo_identificacion=CED&ps_identificacion={}&ps_placa="
    ]

    def __init__(self, search_id: str, *args, **kwargs):
        super(AntSpider, self).__init__(*args, **kwargs)
        # Search ID # 1721194593 1725514119 1721194592 1709026718
        self.search_id = search_id

    def start_requests(self):
        yield Request(
            self.start_urls[0].format(self.search_id),
            callback=self.parse,
            meta={"id": self.search_id},
        )

    def parse(self, response, **kwargs):
        if response.xpath('//td[contains(text(),"LICENCIA TIPO")]/text()'):
            for record in response.xpath('//td[contains(text(),"LICENCIA TIPO")]/text()'):
                ant_item = AntItem()

                ant_item["full_name"] = response.css("table.MarcoTitulo tr td::text").get(
                    ""
                )
                ant_item["id_number"] = (
                    response.xpath('//td[contains(text(),"CED")]/text()')
                    .get("")
                    .split("-")[-1]
                    .strip()
                )
                ant_item["license_type"] = (
                    record.root.split("/")[0].split(":")[-1].split("&")[0].strip()
                )
                ant_item["expedition_date"] = record.root.split("VALIDEZ:")[-1].split(
                    " - "
                )[0]
                ant_item["expiration_date"] = record.root.split("VALIDEZ:")[-1].split(
                    " - "
                )[-1]
                ant_item["points"] = response.xpath(
                    '//td[div[contains(text(),"Puntos")]]/following-sibling::td[1]/text()'
                ).get("")
                ant_item["total"] = ""

                url = "https://consultaweb.ant.gob.ec/PortalWEB/paginas/clientes/clp_estado_cuenta.jsp?ps_persona=738673&ps_id_contrato=&ps_opcion=P&ps_placa=&ps_identificacion={}&ps_tipo_identificacion=CED"

                yield Request(
                    url.format(response.meta["id"]),
                    callback=self.total_value,
                    meta={"item": ant_item},
                    dont_filter=True,
                )
        else:
            item = NotFoundItem()
            item["message"] = "No records were found"
            yield item

    def total_value(self, response):
        item = response.meta["item"]
        item["total"] = (
            response.xpath(
                '//td[font[contains(text(),"TOTAL:")]]/following-sibling::td[1]/font/text()'
            )
            .get("")
            .strip()
        )
        yield item

import httpx
import asyncio
import json
from fake_useragent import UserAgent
from pprint import pprint


async def get_data(search_id: str):
    url_process = "https://api.funcionjudicial.gob.ec/informacion/buscarCausas?page=1&size=30"
    user_agent = UserAgent(os=["windows"], min_percentage=15.0)

    headers = {
        'Accept': 'application/json, text/plain, */*',
        "Accept-Language": "en-US,en;q=0.9,es-EC;q=0.8,es;q=0.7",
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://procesosjudiciales.funcionjudicial.gob.ec',
        'Referer': 'https://procesosjudiciales.funcionjudicial.gob.ec/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': user_agent.random,
        'sec-ch-ua': '"Google Chrome";v="118", "Chromium";v="118", "Not?A_Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        'Cookie': 'CJ=2853568778.31775.0000; Cookie_1=value'
    }

    payload_process = json.dumps({
        "numeroCausa": "",
        "actor": {
            "cedulaActor": search_id,
            "nombreActor": ""
        },
        "demandado": {
            "cedulaDemandado": "",
            "nombreDemandado": ""
        },
        "provincia": "",
        "numeroFiscalia": "",
        "recaptcha": "verdad"
    })

    payload_activity = json.dumps({
        "idMovimientoJuicioIncidente": 23994282,
        "idJuicio": "07U01202200076G",
        "idJudicatura": "07U01",
        "idIncidenteJudicatura": 25219260,
        "aplicativo": "web",
        "nombreJudicatura": "UNIDAD JUDICIAL ESPECIALIZADA DE GARANTÍAS PENITENCIARIAS CON SEDE EN EL CANTÓN MACHALA",
        "incidente": 1
    })

    async with httpx.AsyncClient() as client:
        process_res = await post_api_data(client, url_process, headers, payload_process)

        pprint(process_res)


async def post_api_data(client: httpx.AsyncClient, url: str, headers: dict, payload: dict):
    res = await client.post(url, headers=headers, content=payload)
    return json.loads(res.text)


async def get_api_data(client: httpx.AsyncClient, url: str, headers: dict, target: str):
    res = await client.get(url.format(target), headers=headers)
    return json.loads(res.text)


def run(search_id: str):
    asyncio.run(get_data(search_id))


if __name__ == "__main__":
    run("1709331886")

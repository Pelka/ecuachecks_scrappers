import httpx
import asyncio
import json
from fake_useragent import UserAgent
from dataclasses import dataclass
from pprint import pprint

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


async def post_api_data(client: httpx.AsyncClient, url: str, headers: dict, payload: dict):
    res = await client.post(url, headers=headers, content=payload)
    return res.json()


async def get_api_data(client: httpx.AsyncClient, url: str, headers: dict):
    res = await client.get(url, headers=headers)
    return res.json()


async def get_initial_query(client: httpx.AsyncClient, search_id: str):
    url_process = "https://api.funcionjudicial.gob.ec/informacion/buscarCausas?page=1&size=30"

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

    return await post_api_data(client, url_process, headers, payload_process)


async def parse_data(client: httpx.AsyncClient, processes: list[dict]):
    url = "https://api.funcionjudicial.gob.ec/informacion/getIncidenteJudicatura/{}"
    results = []

    for processes in processes:
        id_judgment = processes.get("idJuicio")
        task = asyncio.create_task(
            get_api_data(client, url.format(id_judgment), headers)
        )
        results.append(task)

    return await asyncio.gather(*results)


async def parse_movements(client: httpx.AsyncClient, movements: list[dict]):
    ulr = "https://api.funcionjudicial.gob.ec/informacion/actuacionesJudiciales"

    payload_activity = json.dumps({
        "idMovimientoJuicioIncidente": 23994282,
        "idJuicio": "07U01202200076G",
        "idJudicatura": "07U01",
        "idIncidenteJudicatura": 25219260,
        "aplicativo": "web",
        "nombreJudicatura": "UNIDAD JUDICIAL ESPECIALIZADA DE GARANTÍAS PENITENCIARIAS CON SEDE EN EL CANTÓN MACHALA",
        "incidente": 1
    })

    for movement in movements:
        pass


async def parse_activities(client: httpx.AsyncClient, activities: dict):
    for activity in activities:
        pass

# for process in processes_response:
#     id_judgment = process.get("idJuicio")
#     movements_response = asyncio.create_task(
#         get_api_data(client, url_movements, headers, id_judgment))
#     fetch_data.append(movements_response)

# fetch_data = await asyncio.gather(*fetch_data)

# # id_judgment = processes_response[0].get("idJuicio")

# # movements_response = await get_api_data(client, url_movements, headers, id_judgment)
# # pprint(movements_response)


async def run(search_id: str):
    async with httpx.AsyncClient() as client:
        result = await get_initial_query(client, search_id)
        movements = await parse_data(client, result)


if __name__ == "__main__":
    asyncio.run(run("1709331886"))

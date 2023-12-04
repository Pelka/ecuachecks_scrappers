# Async libraries
import httpx
import asyncio
# Third-party libraries for enhanced web scraping
from fake_useragent import UserAgent
# Data handling and utility tools
import json
import itertools
from dataclasses import dataclass, asdict, field
from pprint import pprint
# CLI tools and custom modules
from click import command, option
import crawlab

user_agent = UserAgent(os=["windows"], min_percentage=15.0)

proxies = {
    "http://": "http://customer-ecuachecks-cc-ec:Ecuachecks2023@pr.oxylabs.io:7777",
    "https://": "https://customer-ecuachecks-cc-ec:Ecuachecks2023@pr.oxylabs.io:7777"
}

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


@dataclass
class ActivityItem:
    entry_date: str
    title: str
    activity: str


@dataclass
class IncidentItem:
    no_movement: str
    entry_date: str
    actors: list[str] = field(default_factory=str)
    defendants: list[str] = field(default_factory=str)
    activities: list[ActivityItem] = field(default_factory=list)


@dataclass
class MovementItem:
    jurisdiction: str
    city: str
    incidents: list[IncidentItem] = field(default_factory=list)


@dataclass
class ExpelItem:
    no_process: str
    entry_date: str
    matter: str
    action_type: str
    crime_issue: str
    movements: list[MovementItem] = field(default_factory=list)


async def post_api_data(client: httpx.AsyncClient, url: str, headers: dict, payload: dict):
    res = await client.post(url, headers=headers, content=payload)
    return res.json()


async def get_api_data(client: httpx.AsyncClient, url: str, headers: dict):
    res = await client.get(url, headers=headers)
    return res.json()


async def get_initial_query(client: httpx.AsyncClient, search_id: str = None, search_name: str = None):
    url = "https://api.funcionjudicial.gob.ec/informacion/buscarCausas?page=1&size=30"

    temp_payload = {
        "numeroCausa": "",
        "actor": {},
        "demandado": {},
        "provincia": "",
        "numeroFiscalia": "",
        "recaptcha": "verdad"
    }

    payloads = [
        (lambda d, k, v:
            {**d, k: {f"{'cedula' if search_id else 'nombre'}{k.capitalize()}": v}})
        (temp_payload, k, search_id) for k in ["actor", "demandado"]
    ]

    json_payloads = list(map(lambda x: json.dumps(x), payloads))

    results = [
        asyncio.create_task(post_api_data(client, url, headers, payload))
        for payload in json_payloads
    ]

    results = await asyncio.gather(*results)
    return list(itertools.chain(*results))


async def parse_data(client: httpx.AsyncClient, processes: list[dict]):
    for process in processes:
        id_judgment = process.get("idJuicio")
        url = f"https://api.funcionjudicial.gob.ec/informacion/getInformacionJuicio/{id_judgment}"
        result = await get_api_data(client, url, headers)
        item = ExpelItem(
            no_process=id_judgment,
            entry_date=result[0].get("fechaIngreso"),
            matter=result[0].get("nombreMateria"),
            action_type=result[0].get("nombreTipoAccion"),
            crime_issue=result[0].get("nombreDelito")
        )
        await parse_movements(client, item)
        yield item


async def parse_movements(client: httpx.AsyncClient, parent_item: ExpelItem):
    url = f"https://api.funcionjudicial.gob.ec/informacion/getIncidenteJudicatura/{parent_item.no_process}"
    movements = await get_api_data(client, url, headers)

    for movement in movements:
        item = MovementItem(
            city=movement.get("ciudad"),
            jurisdiction=movement.get("nombreJudicatura")
        )

        incidents = movement.get("lstIncidenteJudicatura")

        for incident in incidents:
            sub_item = IncidentItem(
                no_movement=incident.get("incidente"),
                entry_date=incident.get("fechaCrea"),
                actors=[litigante["nombresLitigante"] for litigante in incident["lstLitiganteActor"]
                        ] if incident["lstLitiganteActor"] is not None else [],
                defendants=[litigante["nombresLitigante"] for litigante in incident["lstLitiganteDemandado"]
                            ] if incident["lstLitiganteDemandado"] is not None else []
            )

            payload = json.dumps({
                "idMovimientoJuicioIncidente": incident.get("idMovimientoJuicioIncidente"),
                "idJuicio": parent_item.no_process,
                "idJudicatura": movement.get("idJudicatura"),
                "idIncidenteJudicatura": incident.get("idIncidenteJudicatura"),
                "aplicativo": "web",
                "nombreJudicatura": item.jurisdiction,
                "incidente": sub_item.no_movement,
            }, ensure_ascii=False)

            await parse_activities(client, payload, sub_item)
            item.incidents.append(sub_item)

        parent_item.movements.append(item)


async def parse_activities(client: httpx.Client, payload: str, parent_item: IncidentItem):
    url = "https://api.funcionjudicial.gob.ec/informacion/actuacionesJudiciales"
    activities = await post_api_data(client, url, headers, payload)

    for act in activities:
        item = ActivityItem(
            entry_date=act.get("fecha"),
            title=act.get("tipo"),
            activity=act.get("actividad")
        )
        parent_item.activities.append(item)


async def async_run(search_id: str):
    async with httpx.AsyncClient(proxies=proxies) as client:
        results = await get_initial_query(client, search_id)

        async for res in parse_data(client, results):
            item = asdict(res)
            crawlab.save_item(item)
            pprint(item)


@command()
@option("--search_id", "-s", help="The id (cedula) to scrape")
def cli(search_id):
    # 1709331886
    asyncio.run(async_run(search_id))


cli()

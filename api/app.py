import json
import asyncio
import aiohttp
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional
import time

from robyn import Robyn, Request, WebSocket, WebSocketConnector, ALLOW_CORS, jsonify, Response
# TODO: add auth

app = Robyn(__file__)
ALLOW_CORS(app, origins="GET, POST")

BASE_URL = "http://5.161.59.45:8080/api"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1NDkyNWE3ZjhiZDEwY2ExMzI4ZWQwYyIsIm5iZiI6MTcwMDAyMzU3MCwidXNlcm5hbWUiOiJhZG1pbiJ9.XtOadzJ26oUztwaoLohn2n6FMkNFBsvyM6zjJ-3z5uA"

global_tasks = {}
scrappers = {
    "sri": "65498bddf8bd10ca1328ed83",
    "ant": "65498c25f8bd10ca1328ed85",
    "supa": "65556093f8bd10ca1328ef2c",
    "senescyt": "654e575cf8bd10ca1328ee31",
    "min_educacion": "6557d002f8bd10ca1328f063"
}


@dataclass
class ScpTask:
    id_crawlab: str
    type: str
    status: str


@dataclass
class GlobalTask:
    success: bool
    task_id: str
    total_subtasks: Optional[int] = None
    remaining_subtasks: Optional[int] = None
    status: Optional[str] = None
    error: Optional[str] = None
    data: Optional[list[ScpTask]] = field(default_factory=list)

    def is_completed(self):
        return self.status == "completed"

    def processed(self):
        return self.success == "Ok"


# TODO: handle exceptions
async def start_scrapping_task(session: aiohttp.ClientSession, search_id: str, target: str):
    """
    Starts a scraping task in Crawlab.
    """
    scrapper_id = scrappers.get(target)
    url = f"{BASE_URL}/spiders/{scrapper_id}/run"
    headers = {
        'Authorization': API_TOKEN,
        'Content-Type': 'application/json'
    }
    if target == "ant" or target == "sri":
        payload = {"param": f"search_id={search_id}"}
    else:
        payload = {"param": f"--search_id {search_id}"}

    async with session.post(url, headers=headers, json=payload) as response:
        response = await response.text()
        return {"type": target, "response": json.loads(response)}


async def get_scraper_status(session: aiohttp.ClientSession, scp_task_id: str):
    """
    Retrieves the status of a scraper task from Crawlab.
    """
    url = f"{BASE_URL}/tasks/{scp_task_id}"
    headers = {'Authorization': API_TOKEN}

    try:
        async with session.get(url, headers=headers) as response:
            response = await response.text()
            return json.loads(response)
    except aiohttp.ClientError as e:
        return str(e)


async def get_scraper_data(session: aiohttp.ClientSession, scp_task_id: str):
    """
    Retrieves the data of a scraper task from Crawlab.
    """
    url = f"{BASE_URL}/tasks/{scp_task_id}/data"
    headers = {'Authorization': API_TOKEN}

    try:
        async with session.get(url, headers=headers) as response:
            return await response.text()
    except aiohttp.ClientError as e:
        return str(e)


async def update_scrapper_status(session: aiohttp.ClientSession, scp: ScpTask):
    """
    Updates the status of the scrapper in the task based on Crawlab response.
    """
    result = await get_scraper_status(session, scp.id_crawlab)
    scp.status = result["data"]["status"]
    return scp if scp.status == "finished" or scp.status == "error" else None


async def refine_scrapper_data(session: aiohttp, scp: ScpTask):
    """
    Return the refine data retrived by scrapper, based on Crawlab response.
    """
    result = await get_scraper_data(session, scp.id_crawlab)
    json_result = json.loads(result)
    return {"type": scp.type, "data": json_result["data"]}


async def scrappers_run(session: aiohttp.ClientSession, global_tasks: dict, search_id: str, targets: list):
    total_t = len(targets)
    task_id = uuid.uuid1().hex
    task = GlobalTask(
        success=True,
        status="running",
        task_id=task_id,
        total_subtasks=total_t,
        remaining_subtasks=total_t
    )

    query_tasks = [
        asyncio.create_task(
            start_scrapping_task(session, search_id, target)
        ) for target in targets
    ]
    results = await asyncio.gather(*query_tasks)

    for scp in results:
        scp_task = ScpTask(
            id_crawlab=scp["response"]["data"][0],
            type=scp["type"],
            status="running" if scp["response"]["message"] == "success" else "error"
        )
        task.data.append(scp_task)

    global_tasks[task_id] = task
    return task


async def scrappers_observer(search_id: str, targets: list):
    global global_tasks

    async with aiohttp.ClientSession() as session:
        scp_task = await scrappers_run(session, global_tasks, search_id, targets)
        yield asdict(scp_task)

        while scp_task.remaining_subtasks > 0:
            status_query = [
                asyncio.create_task(
                    update_scrapper_status(session, scp)
                ) for scp in scp_task.data if not (scp.status == "finished" or scp.status == "error")
            ]
            status_res = await asyncio.gather(*status_query)
            status_res = list(
                filter(lambda item: item is not None, status_res))
            finished_scp_tasks = len(status_res)
            global_tasks[scp_task.task_id] = scp_task
            if finished_scp_tasks > 0:
                scp_task.remaining_subtasks = scp_task.remaining_subtasks - finished_scp_tasks

                data_query = [
                    asyncio.create_task(
                        refine_scrapper_data(session, scp)
                    ) for scp in status_res
                ]
                yield await asyncio.gather(*data_query)

            time.sleep(3)


# Web Sockets
websocket = WebSocket(app, "/scrappers")


@websocket.on("connect")
def message(ws: WebSocketConnector):
    return jsonify({
        "client_id": ws.id,
        "socket_name": "scrappers",
        "status": "connection established",
    })


@websocket.on("message")
async def connect(ws: WebSocketConnector, message: str):
    json_mgs = json.loads(message)

    if json_mgs["action"] == "run_follow":
        search_id = json_mgs["params"]["search_id"]
        targets = json_mgs["params"]["targets"]

        async for res in scrappers_observer(search_id, targets):
            ws.async_send_to(ws.id, jsonify(res))

        return "tend"
    else:
        return jsonify({"error": "action not found"})


@websocket.on("close")
async def close():
    return "Goodbye world, from ws"


# @app.get("/scrappers/status/:id")


# @app.get("/scrappers/data/:id")
# async def scrappers_data(request: Request):
#     task_id = request.path_params.get("id")
#     scp_list = scp_tasks[task_id]["scp_list"]

#     async with aiohttp.ClientSession() as session:
#         query_task = [
#             asyncio.create_task(refine_scrapper_data(session, scp)) for scp in scp_list
#         ]

#         result = await asyncio.gather(*query_task)

#     result = list(filter(None, result))

#     return jsonify(result)


if __name__ == "__main__":
    app.start(host='0.0.0.0', port='8088')

import json
import asyncio
import aiohttp
import uuid

from robyn import Robyn
from robyn.robyn import Request, jsonify

# TODO: handle data
# TODO: add auth

app = Robyn(__file__)

scrappers = {
    "sri": "65498bddf8bd10ca1328ed83",
    "ant": "65498c25f8bd10ca1328ed85",
    "supa": "65556093f8bd10ca1328ef2c",
    "senescyt": "654e575cf8bd10ca1328ee31",
    "min_educacion": "6557d002f8bd10ca1328f063"
}

scp_tasks = {}

BASE_URL = "http://5.161.59.45:8080/api"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1NDkyNWE3ZjhiZDEwY2ExMzI4ZWQwYyIsIm5iZiI6MTcwMDAyMzU3MCwidXNlcm5hbWUiOiJhZG1pbiJ9.XtOadzJ26oUztwaoLohn2n6FMkNFBsvyM6zjJ-3z5uA"


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


async def update_scrapper_status(session: aiohttp.ClientSession, scp: dict):
    """
    Updates the status of the scrapper in the task based on Crawlab response.
    """

    if scp["status"] == "running":
        result = await get_scraper_status(session, scp["_id_crawlab"])
        scp["status"] = result["data"]["status"]

    return 0 if scp["status"] == "finished" or scp["status"] == "error" else 1


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


async def refine_scrapper_data(session: aiohttp, scp: dict):
    """
    Return the refine data retrived by scrapper, based on Crawlab response.
    """
    if scp["status"] == "finished":
        result = await get_scraper_data(session, scp["_id_crawlab"])
        json_result = json.loads(result)
        return {"type": scp["type"], "data": json_result["data"]}


@app.post("/scrappers/run/:search_id")
async def scrappers_run(request: Request):
    targets = request.queries.get("targets").split(",")
    search_id = request.path_params.get("search_id")
    task_id = uuid.uuid4().hex

    async with aiohttp.ClientSession() as session:
        query_tasks = [
            asyncio.create_task(
                start_scrapping_task(session, search_id, target)
            ) for target in targets
        ]
        results = await asyncio.gather(*query_tasks)

    scp_tasks[task_id] = {
        "total_tasks": len(targets),
        "remaining_tasks": len(targets),
        "scp_list": []
    }

    for scp in results:
        scp_data = {}
        scp_data["_id_crawlab"] = scp["response"]["data"][0]
        scp_data["type"] = scp["type"]
        if scp["response"]["message"] == "success":
            scp_data["status"] = "running"
        else:
            scp_data["status"] = "retrying"

        scp_tasks[task_id]["scp_list"].append(scp_data)

    return jsonify({"status": "Ok", "id": task_id, "data": scp_tasks[task_id]})


@app.get("/scrappers/status/:id")
async def scrappers_status(request: Request):
    task_id = request.path_params.get("id")
    scp_task = scp_tasks[task_id]
    scp_list = scp_task["scp_list"]

    async with aiohttp.ClientSession() as session:
        query_task = [
            asyncio.create_task(update_scrapper_status(session, scp)) for scp in scp_list
        ]
        result = await asyncio.gather(*query_task)

    scp_task["remaining_tasks"] = sum(result)
    scp_tasks[task_id] = scp_task
    return jsonify(scp_task)


@app.get("/scrappers/data/:id")
async def scrappers_data(request: Request):
    task_id = request.path_params.get("id")
    scp_list = scp_tasks[task_id]["scp_list"]

    async with aiohttp.ClientSession() as session:
        query_task = [
            asyncio.create_task(refine_scrapper_data(session, scp)) for scp in scp_list
        ]

        result = await asyncio.gather(*query_task)

    return jsonify(result)


if __name__ == "__main__":
    app.start(host='0.0.0.0', port='8088')

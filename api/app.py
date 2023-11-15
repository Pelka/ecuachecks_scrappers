# from pymongo import MongoClient
from robyn import Robyn
from robyn.robyn import Request, Response, jsonify
import json
import asyncio
import aiohttp
import uuid
from pprint import pprint

app = Robyn(__file__)

scrappers = {
    "sri": "65498bddf8bd10ca1328ed83",
    "ant": "65498c25f8bd10ca1328ed85"
}

tasks = {}

API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1NDkyNWE3ZjhiZDEwY2ExMzI4ZWQwYyIsIm5iZiI6MTcwMDAyMzU3MCwidXNlcm5hbWUiOiJhZG1pbiJ9.XtOadzJ26oUztwaoLohn2n6FMkNFBsvyM6zjJ-3z5uA"


async def start_in_crawlab(search_id: str, target: str):
    url = f"http://5.161.59.45:8080/api/spiders/{scrappers.get(target)}/run"
    payload = jsonify({"param": f"search_id={search_id}"})
    headers = {
        'Authorization': API_TOKEN,
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            return await response.text()


async def scrapper_status(scp_task_id: str):
    url = f"http://5.161.59.45:8080/api/tasks/{scp_task_id}"
    headers = {
        'Authorization': API_TOKEN,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.text()


async def scrapper_data(scp_task_id: str):
    url = f"http://5.161.59.45:8080/api/tasks/{scp_task_id}/data"
    headers = {
        'Authorization': API_TOKEN,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            return await response.text()


@app.post("/scrappers/run/:search_id")
async def scrappers_run(request: Request) -> str:
    search_id = request.path_params.get("search_id")
    targets = request.queries.get("targets").split(",")
    task_id = uuid.uuid4().hex
    tasks[task_id] = {
        "scrapper_list": []
    }

    for target in targets:
        result = await start_in_crawlab(search_id, target)
        json_result = json.loads(result)
        tasks[task_id]["scrapper_list"].append({
            "type": target,
            "scp_task_id": json_result["data"][0],
            "status": "running"
        })

    # pprint(tasks)

    return jsonify({"status": "Ok", "task_id": task_id})


@app.get("/scrappers/status/:task_id")
async def scrappers_status(request: Request) -> str:
    task_id = request.path_params.get("task_id")
    query_task = tasks[task_id]
    scrappers_list = query_task["scrapper_list"]

    for scrapper in scrappers_list:
        scp_task_id = scrapper.get("scp_task_id")
        result = await scrapper_status(scp_task_id)
        json_result = json.loads(result)
        scrapper["status"] = json_result["data"]["status"]

    tasks[task_id] = query_task
    # pprint(query_task)
    return jsonify(query_task)


@app.get("/scrappers/data/:task_id")
async def scrappers_status(request: Request) -> str:
    task_id = request.path_params.get("task_id")
    scrappers_list = tasks[task_id]["scrapper_list"]
    scrappers_data = {}

    for scrapper in scrappers_list:
        if scrapper["status"] == "finished":
            scp_task_id = scrapper.get("scp_task_id")
            result = await scrapper_data(scp_task_id)
            json_result = json.loads(result)
            scrappers_data[scrapper["type"]] = json_result["data"]

    # pprint(query_task)
    return jsonify(scrappers_data)


if __name__ == "__main__":
    app.start(host='0.0.0.0', port='8088')

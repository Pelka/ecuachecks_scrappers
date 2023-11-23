import asyncio
import aiohttp
import json
from uuid import uuid1
from typing import Optional
from dataclasses import dataclass, field, asdict
from robyn import SubRouter, WebSocket, WebSocketConnector, jsonify

from app import crawlab_api

web_sockets = SubRouter(__file__, "/web_sockets")
scps_socket = WebSocket(web_sockets, "/scrappers")

global_tasks = {}


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


async def start_scrappers(search_id: str, targets: str) -> GlobalTask:
    task_id = uuid1().hex
    total_targets = len(targets)
    task = GlobalTask(
        success=True,
        status="running",
        task_id=task_id,
        total_subtasks=total_targets,
        remaining_subtasks=total_targets
    )

    async with aiohttp.ClientSession() as session:
        fetch_results = [
            asyncio.create_task(
                crawlab_api.run_scrapper(session, search_id, target)
            ) for target in targets
        ]
        results = await asyncio.gather(*fetch_results)

    task.data = [ScpTask(**result) for result in results]
    return task


async def update_subtasks_status(task: GlobalTask) -> list[ScpTask]:
    async def update_finished_subtask(session: aiohttp.ClientSession, subtask: ScpTask):
        subtask.status = await crawlab_api.get_scrapper_status(session, subtask.id_crawlab)
        return subtask if subtask.status in ["finished", "error"] else None

    async with aiohttp.ClientSession() as session:
        fetch_results = [
            asyncio.create_task(
                update_finished_subtask(session, subtask)
            ) for subtask in task.data if subtask.status not in ["finished", "error"]
        ]
        results = await asyncio.gather(*fetch_results)

    return list(filter(lambda item: item is not None, results))


async def fetch_subtask_data(subtasks: list[ScpTask]) -> list[dict]:
    async def set_type(session: aiohttp.ClientSession, subtask: ScpTask):
        data = await crawlab_api.get_scrapper_data(session, subtask.id_crawlab)
        return {"type": subtask.type, "data": data}

    async with aiohttp.ClientSession() as session:
        fetch_results = [
            asyncio.create_task(
                set_type(session, subtask)
            ) for subtask in subtasks
        ]

        return await asyncio.gather(*fetch_results)


async def observer_scrappers(search_id: str, targets: list[str]):
    global global_tasks

    task = await start_scrappers(search_id, targets)
    global_tasks[task.task_id] = task

    yield asdict(task)

    while task.remaining_subtasks > 0:
        completed_subtask = await update_subtasks_status(task)
        total_subtask = len(completed_subtask)
        global_tasks[task.task_id] = task

        if total_subtask > 0:
            task.remaining_subtasks -= total_subtask
            yield await fetch_subtask_data(completed_subtask)

        await asyncio.sleep(3)

    global_tasks[task.task_id].status = "Finished"


@scps_socket.on("connect")
def scrappers_connect(ws: WebSocketConnector):
    return "Connected"


@scps_socket.on("message")
async def scrappers_message(ws: WebSocketConnector, message: str):
    json_mgs = json.loads(message)

    if json_mgs["action"] == "run_follow":
        search_id = json_mgs["params"]["search_id"]
        targets = json_mgs["params"]["targets"]

        async for res in observer_scrappers(search_id, targets):
            ws.async_send_to(ws.id, jsonify(res))

        return "finished"
    else:
        return jsonify({"error": "action not found"})


@scps_socket.on("close")
def scrappers_close(ws: WebSocketConnector):
    return "Connection closed"

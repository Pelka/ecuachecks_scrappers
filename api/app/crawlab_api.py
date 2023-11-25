import aiohttp
from aiohttp import ClientSession


BASE_URL = "http://5.161.59.45:8080/api"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1NDkyNWE3ZjhiZDEwY2ExMzI4ZWQwYyIsIm5iZiI6MTcwMDAyMzU3MCwidXNlcm5hbWUiOiJhZG1pbiJ9.XtOadzJ26oUztwaoLohn2n6FMkNFBsvyM6zjJ-3z5uA"

scrapper_ids = {
    "sri": "65498bddf8bd10ca1328ed83",
    "ant": "65498c25f8bd10ca1328ed85",
    "supa": "65556093f8bd10ca1328ef2c",
    "senescyt": "654e575cf8bd10ca1328ee31",
    "min_educacion": "6557d002f8bd10ca1328f063",
    "expel": "655ed326f8bd10ca1328f49a",
    "min_interior": "655ff325f8bd10ca1328f50e",
    "fis_gen_estado": "65613d03f8bd10ca1328f528"
}

headers = {
    'Authorization': API_TOKEN,
    'Content-Type': 'application/json'
}


async def api_post(session: ClientSession, url: str, payload: dict) -> dict:
    """
    Call the post method on Crawlab
    """
    try:
        async with session.post(url, headers=headers, json=payload) as response:
            return await response.json()

    except aiohttp.ClientError as e:
        raise ConnectionError(
            f"Client error occurred while starting task in Crawlab: {e}")


async def api_get(session: ClientSession, url: str) -> dict:
    """
    Call the get method on Crawlab
    """
    try:
        async with session.get(url, headers=headers) as response:
            return await response.json()

    except aiohttp.ClientError as e:
        raise ConnectionError(
            f"Client error occurred while retrieving status from Crawlab: {e}")


async def run_scrapper(session: ClientSession, search_id: str, target: str) -> dict:
    """
    Initiates a web scraping task for a given target using an asynchronous POST request.

    Parameters:
    - session (ClientSession): The session to use for the HTTP request.
    - search_id (str): The identification card that the scrappers will use.
    - target (str): The target scraper to be invoked.

    Returns:
    - The response from the server after initiating the scraping task.
    """
    scp_id = scrapper_ids.get(target)
    url = f"{BASE_URL}/spiders/{scp_id}/run"

    if target in ["ant", "sri"]:
        payload = {"param": f"search_id={search_id}"}
    else:
        payload = {"param": f"--search_id {search_id}"}

    result = await api_post(session, url, payload)
    result = {
        "id_crawlab": result["data"][0],
        "type": target,
        "status": "running"
    }

    return result


async def get_scrapper_status(session: ClientSession, task_id: str) -> str:
    """
    Retrieves the status of a specific crawlab task.

    Parameters:
    - session (ClientSession): The session to use for the HTTP request.
    - task_id (str): The task id of crawlab.

    Returns:
    - The status of the task as a str.
    """
    url = f"{BASE_URL}/tasks/{task_id}"
    result = await api_get(session, url)
    return result["data"]["status"]


async def get_scrapper_data(session: ClientSession, task_id: str) -> dict:
    """
    Retrieves the data of a specific crawlab task.

    Parameters:
    - session (ClientSession): The session to use for the HTTP request.
    - task_id (str): The task id of crawlab.

    Returns:
    - The data of the task as dict.
    """
    url = f"{BASE_URL}/tasks/{task_id}/data"
    result = await api_get(session, url)
    return result["data"]

# if __name__ == "__main__":
#     import asyncio
#     import pprint

#     async def main():
#         async with ClientSession() as session:
#             res = await get_scrapper_data(session, "655cbe37f8bd10ca1328f367")

#         pprint.pprint(res)

#     asyncio.run(main())

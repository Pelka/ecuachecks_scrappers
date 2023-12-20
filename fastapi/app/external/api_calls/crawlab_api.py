import os
from dotenv import load_dotenv
from dataclasses import dataclass

import httpx

load_dotenv()

scraper_ids = {
    "ant": "65498c25f8bd10ca1328ed85",
    "sri": "65498bddf8bd10ca1328ed83",
    # "expel": "655ed326f8bd10ca1328f49a",
    # "fis_gen_estado": "65613d03f8bd10ca1328f528",
    # "min_educacion": "6557d002f8bd10ca1328f063",
    # "min_interior": "655ff325f8bd10ca1328f50e",
    # "senescyt": "654e575cf8bd10ca1328ee31",
    # "supa": "65556093f8bd10ca1328ef2c",
}


def client_session():
    return httpx.AsyncClient(
        base_url="http://5.161.59.45:8080/api",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": os.getenv("CRAWLAB_TOKEN"),
        },
    )


async def get_data(target_url: str):
    """
    Call the get method
    """
    async with client_session() as session:
        try:
            res = await session.get(f"/{target_url}")
            return res.json()
        except Exception as e:
            print(e)


async def post_data(target_url: str, data: dict | None = None):
    """
    Call the post method
    """
    async with client_session() as session:
        try:
            res = await session.post(f"/{target_url}", json=data)
            return res.json()
        except Exception as e:
            print(e)


async def run_scraper(scraper_target: str, id_number: str) -> dict[str, str]:
    """
    Initiates a scraping task for a given target.

    Parameters:
    - scraper (str): The target scraper to be invoked.
    - id_number (str): The identification card that the scrapers will use.

    Returns:
    - dict: The response from the Crawlab API.
    """

    target_id = scraper_ids.get(scraper_target)

    if scraper_target == "ant" or scraper_target == "sri":
        payload = {"param": f"search_id={id_number}"}
    else:
        payload = {"param": f"--search_id {id_number}"}

    res = await post_data(f"spiders/{target_id}/run", payload)

    return {
        "type": scraper_target,
        "crawlab_id": res["data"][0],
        "status": "running" if res["message"] == "success" else "error",
        "message": res["error"],
    }


async def get_scraper_status(scraper_cwlb_id: str):
    res = await get_data(f"tasks/{scraper_cwlb_id}")
    return res["data"]["status"]


async def get_scraper_data(scraper_cwlb_id: str) -> list[dict]:
    res = await get_data(f"tasks/{scraper_cwlb_id}/data")
    data = res["data"]
    for record in data:
        record.pop("_id")
        record.pop("_tid")
    return data


# async def update_scraper_status(scraper_task: Record):
#     """
#     Update the status of a given scraping task.

#     Parameters:
#     - scraper_id (str): The identification of the crawlab task.

#     Returns:
#     - scraper_task (scraperTaskModel): If the task finished.
#     """
#     res = await get_data(f"tasks/{scraper_task.task_id}")
#     status = res["data"]["status"]

#     if status in ["finished", "error"]:
#         scraper_task.status = status
#         return scraper_task


# async def get_scraper_data(task_id: str):
#     """
#     Retrieves the result of a given scraping task.

#     Parameters:
#     - scraper_id (str): The identification of the crawlab task.

#     Returns:
#     - dict: The response from the Crawlab API.
#     """
#     res = await get_data(f"tasks/{task_id}/data")
#     return res["data"]


# async def fill_scraper_model(scraper_task: Record):
#     """
#     Fill a model using the data from the Crawlab API.
#     """
#     data = await get_scraper_data(scraper_task.id)

#     DataSchema = schemas.get(scraper_task.type)

#     for item in data:
#         scraper_task.data.append(DataSchema(**item))

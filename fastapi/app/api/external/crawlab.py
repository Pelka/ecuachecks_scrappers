import os
from dotenv import load_dotenv
from models import ScrapperTaskModel, schemas

import httpx

load_dotenv()

scrapper_ids = {
    "ant": "65498c25f8bd10ca1328ed85",
    "expel": "655ed326f8bd10ca1328f49a",
    "fis_gen_estado": "65613d03f8bd10ca1328f528",
    "min_educacion": "6557d002f8bd10ca1328f063",
    "min_interior": "655ff325f8bd10ca1328f50e",
    "senescyt": "654e575cf8bd10ca1328ee31",
    "sri": "65498bddf8bd10ca1328ed83",
    "supa": "65556093f8bd10ca1328ef2c",
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


async def run_scrapper(scrapper: str, id_number: str):
    """
    Initiates a scraping task for a given target.

    Parameters:
    - scrapper (str): The target scraper to be invoked.
    - id_number (str): The identification card that the scrappers will use.

    Returns:
    - dict: The response from the Crawlab API.
    """

    scp_id = scrapper_ids.get(scrapper)

    if scrapper == "ant":
        payload = {"param": f"search_id={id_number}"}
    else:
        payload = {"param": f"--search_id {id_number}"}

    res = await post_data(f"spiders/{scp_id}/run", payload)

    return ScrapperTaskModel(id=res["data"][0], type=scrapper, status="running")


async def update_scrapper_status(scrapper_task: ScrapperTaskModel):
    """
    Update the status of a given scraping task.

    Parameters:
    - scrapper_id (str): The identification of the crawlab task.

    Returns:
    - scrapper_task (ScrapperTaskModel): If the task finished.
    """
    res = await get_data(f"tasks/{scrapper_task.task_id}")
    status = res["data"]["status"]

    if status in ["finished", "error"]:
        scrapper_task.status = status
        return scrapper_task


async def get_scrapper_data(task_id: str):
    """
    Retrieves the result of a given scraping task.

    Parameters:
    - scrapper_id (str): The identification of the crawlab task.

    Returns:
    - dict: The response from the Crawlab API.
    """
    res = await get_data(f"tasks/{task_id}/data")
    return res["data"]


async def fill_scrapper_model(scrapper_task: ScrapperTaskModel):
    """
    Fill a model using the data from the Crawlab API.
    """
    data = await get_scrapper_data(scrapper_task.id)

    DataSchema = schemas.get(scrapper_task.type)

    for item in data:
        scrapper_task.data.append(DataSchema(**item))


if __name__ == "__main__":
    import asyncio
    from pprint import pprint
    from models import GlobalTaskModel

    async def main():
        # task = GlobalTaskModel(
        #     id="1",
        #     status="running",
        #     total_subtasks=0,
        #     remaining_subtasks=0,
        #     subtasks=[
        #         ScrapperTaskModel(
        #             id="65682e6bf8bd10ca1328f708",
        #             type="min_interior",
        #             status="running",
        #         )
        #     ],
        # )

        print(await run_scrapper("min_interior", "1718863689"))
        # print(await update_scrapper_status("656814c1f8bd10ca1328f6f6"))
        # pprint(await get_scrapper_data("65682e6bf8bd10ca1328f708"))

        # await fill_scrapper_model(task.subtasks[0])
        # pprint(task.subtasks[0].model_dump())

    asyncio.run(main())

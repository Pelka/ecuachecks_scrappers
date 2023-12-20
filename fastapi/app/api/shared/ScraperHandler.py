from db import crud
from db.database import SessionLocal
from structures import schemas
from external.api_calls import crawlab_api

import asyncio


class ScraperHanlder:
    def __init__(self) -> None:
        self.db = SessionLocal()

    async def start_scrapers(self, scraper_targets: list[str], id_number: str):
        scraper_query = crud.create_scp_query(self.db, schemas.ScraperQueryCreate(status="running"))

        cwlb_call = [
            asyncio.create_task(crawlab_api.run_scraper(target, id_number))
            for target in scraper_targets
        ]

        cwlb_res = await asyncio.gather(*cwlb_call)

        scraper_results = [
            crud.create_scp_result(
                self.db, schemas.ScraperResultCreate(**response), scraper_query.id
            )
            for response in cwlb_res
        ]

        scraper_query.results = scraper_results

        return scraper_query

    async def update_scrapers_status(self):
        pass

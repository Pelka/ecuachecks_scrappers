from db import crud
from db.database import SessionLocal
from structures import schemas
from external.api_calls import crawlab_api
from uuid import UUID

import asyncio


class ScraperHanlder:
    def __init__(self) -> None:
        self.db = SessionLocal()

    async def start_qscp(self, scraper_targets: list[str], id_number: str):
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

    async def update_qscp_result_status(self, query_id: UUID):
        async def update_finished_result(result: schemas.ScraperResult):
            new_status = await crawlab_api.get_scraper_status(result.crawlab_id)
            if new_status in ["finished", "error"]:
                result.status = new_status
                return result

        results = crud.get_scp_results_by_status(self.db, query_id, "running")

        cwlb_call = [asyncio.create_task(update_finished_result(result)) for result in results]
        cwlb_res = await asyncio.gather(*cwlb_call)

        updated_results = list(filter(lambda item: item is not None, cwlb_res))

        for result in updated_results:
            crud.update_scp_result(self.db, result.id, status=result.status)

        return updated_results

    async def retrieve_records_data(self, cwlb_id: str, scraper_type: str, result_id: UUID):
        cwlb_records = await crawlab_api.get_scraper_data(cwlb_id)

        if cwlb_records is None:
            return None

        records = [
            crud.create_scp_record(
                db=self.db,
                record=schemas.ScraperRecordHandler.create(scraper_type, record),
                result_id=result_id,
            )
            for record in cwlb_records
        ]

        return records

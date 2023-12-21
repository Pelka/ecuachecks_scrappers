from db import crud
from db.database import SessionLocal
from sqlalchemy.orm import Session
from structures import schemas
from external.api_calls import crawlab_api
from uuid import UUID

import asyncio


class ScraperHandler:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def start_task(self, scraper_targets: list[str], id_number: str):
        for target in scraper_targets:
            if not schemas.ScraperRecordHandler._validate_schema(
                target, schemas.ScraperRecordHandler.b_schemas
            ):
                raise ValueError(f"Scraper type {target} is not supported")

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

    async def update_status(self, query_id: UUID):
        async def update_finished_result(result: schemas.ScraperResult):
            new_status = await crawlab_api.get_scraper_status(result.crawlab_id)
            if new_status in ["finished", "error"]:
                result.status = new_status
                return result

        results = crud.get_scp_results_by_status(self.db, query_id, "running")

        cwlb_call = [asyncio.create_task(update_finished_result(result)) for result in results]
        cwlb_res = await asyncio.gather(*cwlb_call)

        updated_results = list(filter(None, cwlb_res))

        for result in updated_results:
            crud.update_scp_result(self.db, result.id, status=result.status)

        return updated_results

    async def retrieve_data(self, crawlab_id: str, scraper_type: str, result_id: UUID):
        cwlb_records = await crawlab_api.get_scraper_data(crawlab_id)

        if cwlb_records:
            records = [
                crud.create_scp_record(
                    db=self.db,
                    record=schemas.ScraperRecordHandler.create(scraper_type, record),
                    result_id=result_id,
                )
                for record in cwlb_records
            ]

            return records

    async def run_observer(self, query_id: UUID):
        total_results = len(crud.get_scp_results_by_query_id(self.db, query_id))

        while total_results > 0:
            completed_results = await self.update_status(query_id)
            n_completed = len(completed_results)

            if n_completed > 0:
                for result in completed_results:
                    records = await self.retrieve_data(
                        crawlab_id=result.crawlab_id, scraper_type=result.type, result_id=result.id
                    )

                    if not records:
                        result = crud.update_scp_result(
                            db=self.db, result_id=result.id, message="No records were found"
                        )
                    else:
                        result.records = records

                    yield result

                total_results -= n_completed

        crud.update_scp_query(self.db, query_id, status="finished")

from structures import models, schemas
from db import crud, database

from pprint import pprint
from uuid import UUID

from api.shared.ScraperHandler import ScraperHanlder
from asyncio import run

from external.api_calls import crawlab_api


def main():
    handler = ScraperHanlder()
    db = database.SessionLocal()

    # pprint(run(handler.start_qscp(["ant"], "1725514119")))
    # pprint(run(handler.update_qscp_result_status(UUID("862a35213d304a9fa23920dad0311ef7"))))
    pprint(
        run(
            handler.retrieve_records_data(
                cwlb_id="65834345f8bd10ca1328f748",
                scraper_type="ant",
                result_id=UUID("0adba15b-16a7-4fda-8e5e-8229d9719bdb"),
            )
        )
    )


if __name__ == "__main__":
    main()

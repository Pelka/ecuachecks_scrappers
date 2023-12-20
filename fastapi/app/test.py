from structures import models, schemas
from db import crud, database

from pprint import pprint
from uuid import UUID


def main():
    db = database.SessionLocal()

    records = []

    ant_record = schemas.AntCreate(
        id_number="1234567890",
        full_name="John Doe",
        license_type="A",
        expedition_date="2020-01-01",
        expiration_date="2021-01-01",
        points="10.0",
        total="100.0",
    )

    ant_record_2 = schemas.AntCreate(
        id_number="1234567890",
        full_name="John Doe",
        license_type="B",
        expedition_date="2020-01-01",
        expiration_date="2021-01-01",
        points="10.0",
        total="100.0",
    )

    # records.append(ant_record)
    # records.append(ant_record_2)

    # scraper_query = schemas.ScraperQueryCreate(status="running")
    # scraper_result = schemas.ScraperResultCreate(type="ant")
    # # scraper_result_2 = schemas.ScraperResultCreate(type="ant")

    # res_scp_query = crud.create_scp_query(db, scraper_query)
    # res_scp_result = crud.create_scp_result(db, scraper_result, res_scp_query.id)
    # # res_scp_result_2 = crud.create_scp_result(db, scraper_result_2, res_scp_query.id)

    # results = crud.get_scp_results_by_query_id(db, res_scp_query.id)

    # res_scp_records = [
    #     crud.create_scraper_record(db, record, res_scp_result.id) for record in records
    # ]

    record = crud.get_scp_record(db, UUID("080ad23f5829410e98c1c785fb017211"), "ant")

    pprint(record)


if __name__ == "__main__":
    main()

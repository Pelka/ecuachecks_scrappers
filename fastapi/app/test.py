from structures import models, schemas
from db import crud, database

from pprint import pprint
from uuid import UUID

from api.shared.ScraperHandler import ScraperHanlder
from asyncio import run

from external.api_calls import crawlab_api


def main():
    handler = ScraperHanlder()
    # db = database.SessionLocal()
    # update = crud.update_scp_query(
    #     db=db, query_id=UUID("f480de7ae0894501a917c6ef40594b60"), status="error"
    # )

    # print(update)

    pprint(run(handler.start_scrapers(["ant", "sri"], "1721194593")))


if __name__ == "__main__":
    main()

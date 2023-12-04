from uuid import uuid4
from datetime import datetime, timedelta

from api.app.data_blueprints import models as models


def main():
    new_query = models.ScrapperQuery()
    new_query.id = uuid4()
    new_query.status = "running"
    new_query.creation_date = datetime.now()
    new_query.expired_date = datetime.now() + timedelta(days=7)

    # record1 = data_blueprints.Record()
    # record1.id = uuid4()
    # record1.query_id = new_query.id
    # record1.type = "scrapper"
    # record1.status = "running"
    # record1.message = ""

    # new_query.records.append(record1)

    # with SessionLocal.begin() as session:
    #     session.add(new_query)


if __name__ == "__main__":
    main()

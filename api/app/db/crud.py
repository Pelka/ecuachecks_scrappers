from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from data_desing import models, schemas


def save_obj(db: Session, obj, multy=False):
    if multy:
        db.add_all(obj)
    else:
        db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_scraper_query(db: Session, query: schemas.ScraperQueryCreate):
    db_query = models.ScraperQuery(**query.model_dump())
    save_obj(db, db_query)
    return db_query


def create_scraper_result(
    db: Session, result: schemas.ScraperResultCreate, query_id: UUID
):
    db_result = models.ScraperResult(**result.model_dump(), query_id=query_id)
    save_obj(db, db_result)
    return db_result


def create_scraper_record(
    db: Session, result_id: UUID, record: schemas.ScraperRecordBase
):
    schema_type = record.get_schema_type()
    model = models.ScraperRecordHandler.get_model(schema_type)
    db_record = model(**record.model_dump(), result_id=result_id)
    save_obj(db, db_record)
    return db_record


def create_scraper_task(db: Session, scraper_targets: list[str]):
    scraper_query = create_scraper_query(db, schemas.ScraperQueryCreate(status="started"))
    return [
        create_scraper_result(
            db, schemas.ScraperResultCreate(type=target), query_id=scraper_query.id
        )
        for target in scraper_targets
    ]


# def get_scraper_query(db: Session, query_id: UUID):
#     return (
#         db.query(models.ScraperQuery).filter(models.ScraperQuery.id == query_id).first()
#     )


# def get_scraper_result(db: Session, result_id: UUID):
#     return (
#         db.query(models.ScraperResult)
#         .filter(models.ScraperResult.id == result_id)
#         .first()
#     )


# def get_scraper_record(db: Session, record_id: UUID):
#     return (
#         db.query(models.ScraperRecord)
#         .filter(models.ScraperRecord.id == record_id)
#         .first()
#     )

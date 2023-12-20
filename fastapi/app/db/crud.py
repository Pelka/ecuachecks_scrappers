from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from structures import models, schemas


def save_obj(db: Session, obj, multy=False):
    if multy:
        db.add_all(obj)
    else:
        db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# *==== Query CRUD ====*
def create_scp_query(db: Session, query: schemas.ScraperQueryCreate):
    db_query = models.ScraperQuery(**query.model_dump())
    save_obj(db, db_query)
    return schemas.ScraperQuery.model_validate(db_query.__dict__)


def get_scp_query(db: Session, query_id: UUID):
    db_query = db.query(models.ScraperQuery).filter(models.ScraperQuery.id == query_id).first()
    return schemas.ScraperQuery.model_fields(db_query.__dict__)


# *==== Result CRUD ====*
def create_scp_result(db: Session, result: schemas.ScraperResultCreate, query_id: UUID):
    db_result = models.ScraperResult(**result.model_dump(), query_id=query_id)
    save_obj(db, db_result)
    return schemas.ScraperResult.model_validate(db_result.__dict__)


def get_scp_result(db: Session, result_id: UUID):
    db_result = db.query(models.ScraperResult).filter(models.ScraperResult.id == result_id).first()
    return schemas.ScraperResult.model_validate(db_result.__dict__)


def get_scp_results_by_query_id(db: Session, query_id: UUID):
    db_results = (
        db.query(models.ScraperResult).filter(models.ScraperResult.query_id == query_id).all()
    )
    return [schemas.ScraperResult.model_validate(result.__dict__) for result in db_results]


# *==== Record CRUD ====*
def create_scraper_record(db: Session, record: schemas.ScraperRecordBase, result_id: UUID):
    schema_type = record.get_schema_type()
    model = models.ScraperRecordHandler.get_model(schema_type)
    db_record = model(**record.model_dump(), result_id=result_id)
    save_obj(db, db_record)
    schema = schemas.ScraperRecordHandler.get_schema(schema_type)
    return schema.model_validate(db_record.__dict__)


# def get_scraper_records(db: Session, record_id: UUID, record_type: str):
#     model = models.ScraperRecordHandler.get_model(record_type)
#     return db.query(model).filter(model.id == record_id and model.id).all()


# def create_scraper_task(db: Session, scraper_targets: list[str]):
#     scraper_query = create_scraper_query(db, schemas.ScraperQueryCreate(status="started"))

#     scraper_query.results = [
#         create_scraper_result(
#             db, schemas.ScraperResultCreate(type=target), query_id=scraper_query.id
#         )
#         for target in scraper_targets
#     ]

#     return scraper_query

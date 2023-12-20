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
def create_scp_record(db: Session, record: schemas.ScraperRecordBase, result_id: UUID):
    schema_type = record.get_schema_type()
    model = models.ScraperRecordHandler.get_model(schema_type)
    db_record = model(**record.model_dump(), result_id=result_id)
    schema = schemas.ScraperRecordHandler.get(schema_type)
    save_obj(db, db_record)
    return schema.model_validate(db_record.__dict__)


def get_scp_record(db: Session, record_id: UUID, record_type: str):
    model = models.ScraperRecordHandler.get_model(record_type)
    db_record = db.query(model).filter(model.id == record_id).first()
    schema = schemas.ScraperRecordHandler.get(record_type)
    return schema.model_validate(db_record.__dict__)


def get_scp_records_by_result_id(db: Session, result_id: UUID, record_type: str):
    model = models.ScraperRecordHandler.get_model(record_type)
    db_records = db.query(model).filter(model.result_id == result_id).all()
    schema = schemas.ScraperRecordHandler.get(record_type)
    return [schema.model_validate(record.__dict__) for record in db_records]

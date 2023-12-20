from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from structures import models, schemas


def create(db: Session, model: object, schema: BaseModel, **kwargs):
    try:
        db_obj = model(**schema.model_dump(), **kwargs)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
    except:
        db.rollback()
        raise Exception(f"Error creating object: {model.__name__}")

    return db_obj


def update(db: Session, model: object, obj_id: UUID, **kwargs):
    try:
        db_obj = db.query(model).filter(model.id == obj_id).update(kwargs)
        db.commit()
    except:
        db.rollback()
        raise Exception(f"Error updating object: {model.__name__}")

    return db_obj


# *==== Query CRUD ====*
def create_scp_query(db: Session, query: schemas.ScraperQueryCreate):
    db_query = create(db=db, model=models.ScraperQuery, schema=query)
    return schemas.ScraperQuery.model_validate(db_query.__dict__)


def get_scp_query(db: Session, query_id: UUID):
    db_query = db.query(models.ScraperQuery).filter(models.ScraperQuery.id == query_id).first()
    return schemas.ScraperQuery.model_validate(db_query.__dict__)


def update_scp_query(db: Session, query_id: UUID, **kwargs):
    update(db=db, model=models.ScraperQuery, obj_id=query_id, **kwargs)
    return get_scp_query(db=db, query_id=query_id)


# *==== Result CRUD ====*
def create_scp_result(db: Session, result: schemas.ScraperResultCreate, query_id: UUID):
    db_result = create(db=db, model=models.ScraperResult, schema=result, query_id=query_id)
    return schemas.ScraperResult.model_validate(db_result.__dict__)


def get_scp_result(db: Session, result_id: UUID):
    db_result = db.query(models.ScraperResult).filter(models.ScraperResult.id == result_id).first()
    return schemas.ScraperResult.model_validate(db_result.__dict__)


def get_scp_results_by_query_id(db: Session, query_id: UUID):
    db_results = (
        db.query(models.ScraperResult).filter(models.ScraperResult.query_id == query_id).all()
    )
    return [schemas.ScraperResult.model_validate(result.__dict__) for result in db_results]


def update_scp_result(db: Session, result_id: UUID, **kwargs):
    update(db=db, model=models.ScraperResult, obj_id=result_id, **kwargs)
    return get_scp_result(db=db, result_id=result_id)


# *==== Record CRUD ====*
def create_scp_record(db: Session, record: schemas.ScraperRecordBase, result_id: UUID):
    schema_type = record.get_schema_type()
    db_record = create(
        db=db,
        model=models.ScraperRecordHandler.get_model(schema_type),
        schema=record,
        result_id=result_id,
    )
    return schemas.ScraperRecordHandler.get(schema_type).model_validate(db_record.__dict__)


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

from sqlalchemy import Column, Integer, Boolean, Float, String, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.ext.declarative import declared_attr

import re
from uuid import uuid4
from datetime import datetime

from db.database import DeclarativeBase


# *==== Base Models & Mixins ====*
class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)


class ScraperMixin(object):
    @declared_attr
    def result_id(cls):
        return mapped_column("result_id", ForeignKey("scraper_result.id"), index=True)

    @declared_attr
    def result(cls):
        return relationship("ScraperResult")


# *==== Query Models ====*
class ScraperQuery(Base):
    status = Column(String)
    creation_date = Column(DateTime)
    expired_date = Column(DateTime)

    results = relationship("ScraperResult", back_populates="query")


class ScraperResult(Base):
    type = Column(String, nullable=False)
    status = Column(String)
    message = Column(String, nullable=True, default=None)

    query_id = mapped_column(ForeignKey("scraper_query.id"), index=True)
    query = relationship("ScraperQuery", back_populates="results")


# *==== Simple Scraper Models ====*
class Ant(ScraperMixin, Base):
    id_number = Column(String)
    full_name = Column(String)
    license_type = Column(String)
    expedition_date = Column(DateTime)
    expiration_date = Column(DateTime)
    points = Column(Float)
    total = Column(Float)


class Sri(ScraperMixin, Base):
    id_number = Column(String)
    full_name = Column(String)
    message = Column(String)
    disputed_debts = Column(DECIMAL(19, 4))
    firm_debts = Column(DECIMAL(19, 4))
    payment_facilities = Column(DECIMAL(19, 4))


class MinEducacion(ScraperMixin, Base):
    id_number = Column(String)
    full_name = Column(String)
    no = Column(Integer)
    college = Column(String)
    degree = Column(String)
    speciality = Column(String)
    graduation_date = Column(DateTime)


class MinInterior(ScraperMixin, Base):
    id_number = Column(String)
    full_name = Column(String)
    doc_type = Column(String)
    background = Column(Boolean)
    certificate = Column(String)


class Supa(ScraperMixin, Base):
    legal_representative = Column(String)
    primary_obligator = Column(String)
    judicial_process = Column(String)
    province = Column(String)
    jurisdictional_depency = Column(String)
    card_code = Column(String)
    type = Column(String)
    n_pending_alimony = Column(Integer)
    n_other_debts = Column(Integer)
    current_payment = Column(DECIMAL(19, 4))
    subtotal_alimony_payments = Column(DECIMAL(19, 4))
    subtotal_alimony_taxes = Column(DECIMAL(19, 4))
    total_alimony_paytax = Column(DECIMAL(19, 4))
    total_other_debts = Column(DECIMAL(19, 4))
    total = Column(DECIMAL(19, 4))


class SuperintAdmin(ScraperMixin, Base):
    appoinment_date = Column(DateTime)
    article = Column(Integer)
    com_reg_date = Column(DateTime)
    com_reg_number = Column(String)
    end_date = Column(DateTime)
    id_file = Column(String)
    lr_a = Column(String)
    name = Column(String)
    nationality = Column(String)
    period = Column(Integer)
    position = Column(String)
    ruc = Column(String)


class SuperintShareholder(ScraperMixin, Base):
    effective_possession = Column(DECIMAL(19, 4))
    id_file = Column(Integer)
    invested_capital = Column(DECIMAL(19, 4))
    legal_status = Column(String)
    name = Column(String)
    nominal_value = Column(DECIMAL(19, 4))
    ruc = Column(String)
    total_company_capital = Column(DECIMAL(19, 4))


# *==== Complex Scraper Models ====*
class Senescyt(ScraperMixin, Base):
    id_number = Column(String)
    full_name = Column(String)
    gender = Column(Boolean)
    nationality = Column(String)

    degrees = relationship("SenescytDegree", back_populates="parent")


class SenescytDegree(Base):
    title = Column(String)
    college = Column(String)
    type = Column(String)
    recognized_by = Column(String)
    register_num = Column(String)
    register_date = Column(DateTime)
    area = Column(String)
    note = Column(String)

    id_senescyt = mapped_column(ForeignKey("senescyt.id"), index=True)
    parent = relationship("Senescyt", back_populates="degrees")


class FisEstado(ScraperMixin, Base):
    attorney = Column(String)
    no_process = Column(String)
    province = Column(String)
    date_time = Column(DateTime)
    state = Column(String)
    office = Column(String)
    crime = Column(String)
    unit = Column(String)

    involveds = relationship("FisEstadolInvolved", back_populates="parent")


class FisEstadolInvolved(Base):
    id_number = Column(String)
    full_name = Column(String)
    status = Column(String)

    id_fis_estado = mapped_column(ForeignKey("fis_estado.id"), index=True)
    parent = relationship("FisEstado", back_populates="involveds")


class ScraperRecordHandler:
    models = {
        "ant": Ant,
        "sri": Sri,
        "min_educacion": MinEducacion,
        "min_interior": MinInterior,
        "supa": Supa,
        "superint_admin": SuperintAdmin,
        "superint_shareholder": SuperintShareholder,
        "senescyt": Senescyt,
        "fis_estado": FisEstado,
    }

    @staticmethod
    def _validate_model(model_type: str, in_dict: dict):
        if model_type not in in_dict.keys():
            raise ValueError(f"{model_type} is not a valid model type")

    @classmethod
    def get_model(cls, model_type: str):
        cls._validate_model(model_type, cls.models)
        return cls.models.get(model_type)

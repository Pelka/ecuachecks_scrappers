from sqlalchemy import Column, Integer, Boolean, Float, String, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL, UUID
from sqlalchemy.orm import relationship

from uuid import uuid4
from datetime import datetime

from db.Base import Base


# * Query models *
class ScrapperQuery(Base):
    __tablename__ = "scrapper_query"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    status = Column(String)
    creation_date = Column(DateTime, default=datetime.now)
    expired_date = Column(DateTime)

    records = relationship("ScrappedResult", back_populates="query")


class ScrappedResult(Base):
    __tablename__ = "query_result"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("query.id"), index=True)
    type = Column(String)
    status = Column(String)
    message = Column(String)

    query = relationship("ScrapperQuery", back_populates="records")


# * Scrappers -> simple models *
class ScrapperBase(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_result = Column(UUID(as_uuid=True), index=True)


class Ant(ScrapperBase):
    __tablename__ = "ant"

    id_number = Column(String)
    full_name = Column(String)
    license_type = Column(String)
    expedition_date = Column(DateTime)
    expiration_date = Column(DateTime)
    points = Column(Float)
    total = Column(Float)


class Sri(ScrapperBase):
    __tablename__ = "sri"

    id_number = Column(String)
    full_name = Column(String)
    message = Column(String)
    disputed_debts = Column(DECIMAL(19, 4))
    firm_debts = Column(DECIMAL(19, 4))
    payment_facilities = Column(DECIMAL(19, 4))


class MinEducacion(ScrapperBase):
    __tablename__ = "min_educacion"

    id_number = Column(String)
    full_name = Column(String)
    no = Column(Integer)
    college = Column(String)
    degree = Column(String)
    speciality = Column(String)
    graduation_date = Column(DateTime)


class MinInterior(ScrapperBase):
    __tablename__ = "min_interior"

    id_number = Column(String)
    full_name = Column(String)
    doc_type = Column(String)
    background = Column(Boolean)
    certificate = Column(String)


class Supa(Base):
    __tablename__ = "supa"

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


class superintendenciaAdmin(Base):
    __tablename__ = "superintendencia_administracion"

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


class superintenciaShareholder(Base):
    __tablename__ = "superintendencia_shareholder"

    effective_possession = Column(DECIMAL(19, 4))
    id_file = Column(Integer)
    invested_capital = Column(DECIMAL(19, 4))
    legal_status = Column(String)
    name = Column(String)
    nominal_value = Column(DECIMAL(19, 4))
    ruc = Column(String)
    total_company_capital = Column(DECIMAL(19, 4))


# * Scrappers -> complex models *
class Senescyt(Base):
    __tablename__ = "senescyt"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_record = Column(UUID(as_uuid=True), ForeignKey("record.id"), index=True)
    id_number = Column(String)
    full_name = Column(String)
    gender = Column(Boolean)
    nationality = Column(String)


class SenescyDegree(Base):
    __tablename__ = "senescyt_degree"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_senescyt = Column(UUID(as_uuid=True), ForeignKey("senescyt.id"), index=True)
    title = Column(String)
    college = Column(String)
    type = Column(String)
    recognized_by = Column(String)
    register_num = str
    register_date = Column(DateTime)
    area = Column(String)
    note = Column(String)


class FiscaliaEstado(Base):
    __tablename__ = "fis_estado"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_record = Column(UUID(as_uuid=True), ForeignKey("record.id"), index=True)
    attorney = Column(String)
    no_process = Column(String)
    province = Column(String)
    date_time = Column(DateTime)
    state = Column(String)
    office = Column(String)
    crime = Column(String)
    unit = Column(String)


class FiscaliaEstadolInvolved(Base):
    __tablename__ = "fis_estado_involved"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_fis_estado = Column(
        UUID(as_uuid=True), ForeignKey("fis_gen_estado.id"), index=True
    )
    id_number = Column(String)
    full_name = Column(String)
    status = Column(String)

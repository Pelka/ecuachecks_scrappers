from sqlalchemy import Column, Integer, Boolean, Float, String, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL, UUID
from sqlalchemy.orm import relationship
from uuid import uuid4

from db.Base import Base


class Ant(Base):
    __tablename__ = "ant"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_record = Column(UUID(as_uuid=True), ForeignKey("scrapper_task.id"), index=True)
    id_number = Column(String)
    full_name = Column(String)
    license_type = Column(String)
    expedition_date = Column(DateTime)
    expiration_date = Column(DateTime)
    points = Column(Float)
    total = Column(Float)


class Sri(Base):
    __tablename__ = "sri"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_record = Column(UUID(as_uuid=True), ForeignKey("scrapper_task.id"), index=True)
    id_number = Column(String)
    full_name = Column(String)
    message = Column(String)
    disputed_debts = Column(DECIMAL(19, 4))
    firm_debts = Column(DECIMAL(19, 4))
    payment_facilities = Column(DECIMAL(19, 4))


class MinEducacion(Base):
    __tablename__ = "min_educacion"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_record = Column(UUID(as_uuid=True), ForeignKey("scrapper_task.id"), index=True)
    no = Column(Integer)
    id_number = Column(String)
    full_name = Column(String)
    college = Column(String)
    degree = Column(String)
    speciality = Column(String)
    graduation_date = Column(DateTime)


class MinInterior(Base):
    __tablename__ = "min_interior"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_record = Column(UUID(as_uuid=True), ForeignKey("scrapper_task.id"), index=True)
    id_number = Column(String)
    full_name = Column(String)
    doc_type = Column(String)
    background = Column(Boolean)
    certificate = Column(String)


class Supa(Base):
    __tablename__ = "supa"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_record = Column(UUID(as_uuid=True), ForeignKey("scrapper_task.id"), index=True)
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


class Senescyt(Base):
    __tablename__ = "senescyt"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_record = Column(UUID(as_uuid=True), ForeignKey("scrapper_task.id"), index=True)
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
    id_record = Column(UUID(as_uuid=True), ForeignKey("scrapper_task.id"), index=True)
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


class superintendenciaAdmin(Base):
    __tablename__ = "superintendencia_administracion"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_record = Column(UUID(as_uuid=True), ForeignKey("scrapper_task.id"), index=True)
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

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    id_record = Column(UUID(as_uuid=True), ForeignKey("scrapper_task.id"), index=True)
    effective_possession = Column(DECIMAL(19, 4))
    id_file = Column(Integer)
    invested_capital = Column(DECIMAL(19, 4))
    legal_status = Column(String)
    name = Column(String)
    nominal_value = Column(DECIMAL(19, 4))
    ruc = Column(String)
    total_company_capital = Column(DECIMAL(19, 4))

# Data validation
from typing import Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

# Model
from pydantic import BaseModel, Field, field_validator

# Validators
from validators import CleaningValidators as cv


# * Query schemas *
class TaskBase(BaseModel):
    id: UUID = Field(default_factory=uuid4())
    status: str


class Record(BaseModel):
    type: str
    message: Optional[str] = ""
    data: list[Any] = Field(default_factory=list)


class Query(TaskBase):
    subtasks: list[Record] = Field(default_factory=list)
    creation_date: datetime = Field(default_factory=datetime.now)
    expide_date: datetime
    total_subtasks: int
    remaining_subtasks: int


# * Scrappers -> simple schemas *
class NotFound(BaseModel):
    message: str


# --> ANT
class Ant(BaseModel):
    id_number: str
    full_name: str
    license_type: str
    expedition_date: cv.FormatedDatetime
    expiration_date: cv.FormatedDatetime
    points: cv.StrToFloat
    total: cv.StrToFloat


# --> SRI
class Sri(BaseModel):
    id_number: str
    full_name: str
    message: str
    disputed_debts: cv.StrToDecimal
    firm_debts: cv.StrToDecimal
    payment_facilities: cv.StrToDecimal


# --> Ministerio de Educacion
class MinEducacion(BaseModel):
    no: int
    id_number: str
    full_name: str
    college: cv.CapitalizedPhrase
    degree: cv.CapitalizedPhrase
    speciality: cv.CapitalizedPhrase
    graduation_date: cv.FormatedDate


# --> Ministerio del Interior
class MinInterior(BaseModel):
    full_name: str
    id_number: str
    doc_type: cv.CapitalizedPhrase
    background: bool
    certificate: str

    @field_validator("background", mode="before")
    @classmethod
    def background_to_bool(cls, value):
        return True if value == "SI" else False


# --> SUPA
class SUPA(BaseModel):
    legal_representative: str
    primary_obligator: str
    judicial_process: str
    province: cv.CapitalizedPhrase
    jurisdictional_depency: str
    card_code: str
    type: str
    n_pending_alimony: cv.StrToInt
    n_other_debts: cv.StrToInt
    current_payment: cv.MoneyToDecimal
    subtotal_alimony_payments: cv.MoneyToDecimal
    subtotal_alimony_taxes: cv.MoneyToDecimal
    total_alimony_paytax: cv.MoneyToDecimal
    total_other_debts: cv.MoneyToDecimal
    total: cv.MoneyToDecimal


# * Scrappers -> complex schemas *
# --> Senescyt Degree
class SenescytDegree(BaseModel):
    title: cv.CapitalizedPhrase
    college: cv.CapitalizedPhrase
    type: str
    recognized_by: str
    register_num: str
    register_date: cv.FormatedDate
    area: cv.CapitalizedPhrase
    note: str


# --> Senescyt
class Senescyt(BaseModel):
    id_number: str
    full_name: str
    gender: cv.GenderBool
    nacionality: cv.StrToCapitalize
    degress: list[SenescytDegree] = Field(default_factory=list)


# --> Fiscalia General del Estado Involved
class FiscaliaEstadoInvolved(BaseModel):
    id_number: str
    full_name: str
    status: cv.StrToCapitalize


# --> Fiscalia General del Estado
class FiscaliaEstado(BaseModel):
    attorney: cv.CapitalizedPhrase
    no_process: str
    province: cv.CapitalizedPhrase
    date_time: cv.FormatedDatetime
    state: cv.CapitalizedPhrase
    office: str
    crime: str
    unit: cv.CapitalizedPhrase
    involveds: list[FiscaliaEstadoInvolved] = Field(default_factory=list)

    @field_validator("attorney", mode="before")
    def split_attorney(cls, value):
        return value.split(": ")[1]


# --> Superintendia Administration
class SuperintendenciaAdmin(BaseModel):
    appointment_date: cv.FormatedDatetime
    article: cv.StrToInt
    com_reg_date: cv.FormatedDatetime
    com_reg_number: cv.StrToInt
    end_date: cv.FormatedDatetime
    id_file: str
    lr_a: str
    name: str
    nationality: str
    period: cv.StrToInt
    position: str
    ruc: str


# --> Superintendia Shareholder
class SuperintendenciaShareholder(BaseModel):
    effective_possession: cv.StrToDecimal
    id_file: int
    invested_capital: cv.StrToDecimal
    legal_status: str
    name: str
    nominal_value: cv.StrToDecimal
    ruc: str
    total_company_capital: cv.StrToDecimal


# --> Superintendia
class Superintendencia(BaseModel):
    current_administration: list[SuperintendenciaAdmin] = Field(default_factory=list)
    current_shareholder: list[SuperintendenciaShareholder] = Field(default_factory=list)


SCRAPPER_SCHEMAS = {
    "not_found": NotFound,
    "ant": Ant,
    "sri": Sri,
    "supa": Superintendencia,
    "senescyt": Senescyt,
    "fis_gen_estado": FiscaliaEstado,
    "min_educacion": MinEducacion,
    "min_interior": MinInterior,
}

# Data validation
from typing import Optional, Type, Dict
from typing_extensions import Unpack
from decimal import Decimal
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import re

# Model
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict

# Validators
from structures.validators import CleaningValidators as cv


# *==== Query Schemas ====*
# -> Scraper Query
class ScraperQueryBase(BaseModel):
    status: str
    creation_date: datetime
    expired_date: datetime


class ScraperQueryCreate(ScraperQueryBase):
    creation_date: datetime = Field(default_factory=datetime.now)
    expired_date: datetime = Field(default_factory=lambda: datetime.now() + timedelta(days=7))


class ScraperQuery(ScraperQueryBase):
    id: UUID
    results: Optional[list] = Field(default_factory=list)

    class Config:
        from_atrributes = True


# --> Scraper Result
class ScraperResultBase(BaseModel):
    crawlab_id: str
    type: str
    status: str
    message: Optional[str] = Field(default=None)


class ScraperResultCreate(ScraperResultBase):
    pass


class ScraperResult(ScraperResultBase):
    id: UUID
    query_id: UUID

    class Config:
        from_atrributes = True


# # *==== Simple Scraper Schemas ====*
class NotFoundRecord(BaseModel):
    message: str


class ScraperRecordBase(BaseModel):
    @classmethod
    def get_schema_type(cls):
        scraper_type = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        if "_create" in scraper_type:
            scraper_type = scraper_type.split("_create")[0]
        return scraper_type


class ScraperRecord(BaseModel):
    id: UUID
    result_id: UUID

    class Config:
        from_atrributes = True


# --> ANT
class AntBase(ScraperRecordBase):
    id_number: str
    full_name: str
    license_type: str
    expedition_date: datetime
    expiration_date: datetime
    points: float
    total: float


class AntCreate(AntBase):
    expedition_date: cv.FormattedDatetime
    expiration_date: cv.FormattedDatetime
    points: cv.StrToFloat
    total: cv.StrToFloat


class Ant(AntBase, ScraperRecord):
    pass


# --> SRI
class SriBase(ScraperRecordBase):
    id_number: str
    full_name: str
    message: str
    disputed_debts: Decimal
    firm_debts: Decimal
    payment_facilities: Decimal


class SriCreate(SriBase):
    disputed_debts: cv.StrToDecimal
    firm_debts: cv.StrToDecimal
    payment_facilities: cv.StrToDecimal


class Sri(SriBase, ScraperRecord):
    pass


class ScraperRecordHandler:
    schemas: Dict[str, Type[ScraperRecordBase]] = {
        "not_found": NotFoundRecord,
        "ant": Ant,
        "sri": Sri,
    }

    b_schemas: Dict[str, Type[ScraperRecordBase]] = {
        "ant": AntBase,
        "sri": SriBase,
    }

    c_schemas: Dict[str, Type[ScraperRecordBase]] = {
        "ant": AntCreate,
        "sri": SriCreate,
    }

    @staticmethod
    def _validate_schema(schema_type: str, in_dict: dict):
        if schema_type not in in_dict.keys():
            raise ValueError(f"{schema_type} is not valid schema record")
        return True

    @classmethod
    def get(cls, schema_type: str):
        cls._validate_schema(schema_type, cls.schemas)
        return cls.schemas.get(schema_type)

    @classmethod
    def get_base(cls, schema_type: str):
        cls._validate_schema(schema_type, cls.b_schemas)
        return cls.b_schemas.get(schema_type)

    @classmethod
    def create(cls, schema_type: str, data: dict):
        schema = cls.get_base(schema_type)

        if data.keys() != schema.model_fields.keys():
            raise ValueError(
                f"Provided data has invalid fields \n {data.keys()} \n {list(schema.model_fields.keys())}"
            )

        c_schema = cls.c_schemas.get(schema_type)
        return c_schema(**data)


# # --> Ministerio de Educacion
# class MinEducacion(BaseSchema):
#     id_number: str
#     full_name: str
#     no: int
#     college: cv.CapitalizedPhrase
#     degree: cv.CapitalizedPhrase
#     speciality: cv.CapitalizedPhrase
#     graduation_date: cv.FormatedDate


# # --> Ministerio del Interior
# class MinInterior(BaseSchema):
#     full_name: str
#     id_number: str
#     doc_type: cv.CapitalizedPhrase
#     background: bool
#     certificate: str

#     @field_validator("background", mode="before")
#     @classmethod
#     def background_to_bool(cls, value):
#         return True if value == "SI" else False


# # --> SUPA
# class Supa(BaseSchema):
#     legal_representative: str
#     primary_obligator: str
#     judicial_process: str
#     province: cv.CapitalizedPhrase
#     jurisdictional_depency: str
#     card_code: str
#     type: str
#     n_pending_alimony: cv.StrToInt
#     n_other_debts: cv.StrToInt
#     current_payment: cv.MoneyToDecimal
#     subtotal_alimony_payments: cv.MoneyToDecimal
#     subtotal_alimony_taxes: cv.MoneyToDecimal
#     total_alimony_paytax: cv.MoneyToDecimal
#     total_other_debts: cv.MoneyToDecimal
#     total: cv.MoneyToDecimal


# # --> Superintencia Shareholder
# class SuperintShareholder(BaseModel):
#     effective_possession: cv.StrToDecimal
#     id_file: int
#     invested_capital: cv.StrToDecimal
#     legal_status: str
#     name: str
#     nominal_value: cv.StrToDecimal
#     ruc: str
#     total_company_capital: cv.StrToDecimal


# # -> Superintencia Admin
# class SuperintAdmin(BaseSchema):
#     appointment_date: cv.FormatedDatetime
#     article: cv.StrToInt
#     com_reg_date: cv.FormatedDatetime
#     com_reg_number: cv.StrToInt
#     end_date: cv.FormatedDatetime
#     id_file: str
#     lr_a: str
#     name: str
#     nationality: str
#     period: cv.StrToInt
#     position: str
#     ruc: str


# # --> Superintendia
# class Superintendencia(BaseModel):
#     current_admin: list[SuperintAdmin] = Field(default_factory=list)
#     current_shareholder: list[SuperintShareholder] = Field(default_factory=list)


# # *==== Complex Scraper Schemas ====*
# # # --> Senescyt Degree
# class SenescytDegree(BaseSchema):
#     title: cv.CapitalizedPhrase
#     college: cv.CapitalizedPhrase
#     type: str
#     recognized_by: str
#     register_num: str
#     register_date: cv.FormatedDate
#     area: cv.CapitalizedPhrase
#     note: str


# # --> Senescyt
# class Senescyt(BaseSchema):
#     id_number: str
#     full_name: str
#     gender: cv.GenderBool
#     nacionality: cv.StrToCapitalize
#     degress: list[SenescytDegree] = Field(default_factory=list)


# # --> Fiscalia General del Estado Involved
# class FiscaliaEstadoInvolved(BaseSchema):
#     id_number: str
#     full_name: str
#     status: cv.StrToCapitalize


# # --> Fiscalia General del Estado
# class FiscaliaEstado(BaseModel):
#     attorney: cv.CapitalizedPhrase
#     no_process: str
#     province: cv.CapitalizedPhrase
#     date_time: cv.FormatedDatetime
#     state: cv.CapitalizedPhrase
#     office: str
#     crime: str
#     unit: cv.CapitalizedPhrase
#     involveds: list[FiscaliaEstadoInvolved] = Field(default_factory=list)

#     @field_validator("attorney", mode="before")
#     def split_attorney(cls, value):
#         return value.split(": ")[1]

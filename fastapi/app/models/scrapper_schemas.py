from pydantic import BaseModel, validator, Field
from datetime import datetime
from decimal import Decimal


### SIMPLE SCHEMAS ###
# --> In case when the data is not found
class NotFound(BaseModel):
    message: str


# --> ANT
class Ant(BaseModel):
    id_number: str
    full_name: str
    license_type: str
    expedition_date: datetime
    expiration_date: datetime
    points: float
    total: float

    @validator("expedition_date", "expiration_date", pre=True)
    def date_to_datetime(cls, value):
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    @validator("points", "total", pre=True)
    def str_to_float(cls, value):
        return float(value)


# --> SRI
class Sri(BaseModel):
    id_number: str
    full_name: str
    message: str
    disputed_debts: Decimal
    firm_debts: Decimal
    payment_facilities: Decimal

    @validator("firm_debts", "disputed_debts", "payment_facilities", pre=True)
    def str_to_decimal(cls, value):
        return Decimal(value)


# --> Ministerio de Educacion
class MinEducacion(BaseModel):
    no: int
    id_number: str
    full_name: str
    college: str
    degree: str
    speciality: str
    graduation_date: datetime

    @validator("graduation_date", pre=True)
    def date_to_datetime(cls, value):
        return datetime.strptime(value, "%Y-%m-%d")

    @validator("college", "degree", "speciality", pre=True)
    def upper_to_capitalize(cls, value):
        return " ".join([word.capitalize() for word in value.split(" ")])


# --> Ministerio del Interior
class MinInterior(BaseModel):
    full_name: str
    id_number: str
    doc_type: str
    background: bool
    certificate: str

    @validator("background", pre=True)
    def background_to_bool(cls, value):
        return True if value == "SI" else False

    @validator("doc_type", pre=True)
    def upper_to_capitalize(cls, value):
        return " ".join([word.capitalize() for word in value.split(" ")])


# --> SUPA
class SUPA(BaseModel):
    legal_representative: str
    primary_obligator: str
    judicial_process: str
    province: str
    jurisdictional_depency: str
    card_code: str
    type: str
    n_pending_alimony: int
    n_other_debts: int
    current_payment: Decimal
    subtotal_alimony_payments: Decimal
    subtotal_alimony_interest: Decimal
    total_alimony_payint: Decimal
    total_other_debts: Decimal
    total: Decimal

    @validator("n_pending_alimony", "n_other_debts", pre=True)
    def str_to_int(cls, value):
        return int(value)

    @validator("province", pre=True)
    def upper_to_capitalize(cls, value):
        return " ".join([word.capitalize() for word in value.split(" ")])

    @validator(
        "current_payment",
        "subtotal_alimony_payments",
        "subtotal_alimony_interest",
        "total_alimony_payint",
        "total_other_debts",
        "total",
        pre=True,
    )
    def str_to_decimal(cls, value):
        spplited_value = value.split("$")
        return Decimal(spplited_value[1])


### COMPLEX SCHEMAS ###
# --> Senescyt Degree
class SenescytDegree(BaseModel):
    title: str
    college: str
    type: str
    recognized: str
    register_num: str
    register_date: datetime
    area: str
    note: str

    @validator("register_date", pre=True)
    def date_to_datetime(cls, value):
        return datetime.strptime(value, "%Y-%m-%d")

    @validator("title", "college", "area", pre=True)
    def upper_to_capitalize(cls, value):
        return " ".join([word.capitalize() for word in value.split(" ")])


# --> Senescyt
class Senescyt(BaseModel):
    id_number: str
    full_name: str
    gender: bool
    nacionality: str
    degress: list[SenescytDegree] = Field(default_factory=list)

    @validator("gender", pre=True)
    def gender_to_bool(cls, value):
        return True if value == "MASCULINO " else False

    @validator("nacionality", pre=True)
    def upper_to_capitalize(cls, value):
        return value.capitalize()


# --> Fiscalia General del Estado Involved
class FiscaliaGeneralInvolved(BaseModel):
    id_number: str
    full_name: str
    status: str

    @validator("status", pre=True)
    def upper_to_capitalize(cls, value):
        return value.capitalize()


# --> Fiscalia General del Estado
class FiscaliaGeneral(BaseModel):
    attorney: str
    no_process: str
    province: str
    date_time: datetime
    state: str
    office: str
    crime: str
    unit: str
    people: list[FiscaliaGeneralInvolved] = Field(default_factory=list)

    @validator("date", pre=True)
    def date_to_datetime(cls, value):
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    @validator("attorney", pre=True)
    def split_attorney(cls, value):
        return value.split(": ")[1]

    @validator("place", "state", "unit", "attorney", pre=True)
    def upper_to_capitalize(cls, value):
        return " ".join([word.capitalize() for word in value.split(" ")])


# --> Superintendia Administration
class SuperintendenciaAdmin(BaseModel):
    appointment_date: datetime
    article: int
    com_reg_date: datetime
    com_reg_number: int
    end_date: datetime
    id_file: str
    lr_a: str
    name: str
    nationality: str
    period: int
    position: str
    ruc: str

    @validator("article", "com_reg_number", "period", pre=True)
    def str_to_int(cls, value):
        return int(value)

    @validator("appointment_date", "com_reg_date", "end_date", pre=True)
    def date_to_datetime(cls, value):
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if value else ""


# --> Superintendia Shareholder
class SuperintendenciaShareholder(BaseModel):
    effective_possession: str
    id_file: int
    invested_capital: Decimal
    legal_status: str
    name: str
    nominal_value: Decimal
    ruc: str
    total_company_capital: Decimal

    @validator("invested_capital", "total_company_capital", "nominal_value", pre=True)
    def str_to_decimal(cls, value):
        return Decimal(value)


# --> Superintendia
class Superintendencia(BaseModel):
    current_administration: list[SuperintendenciaAdmin] = Field(default_factory=list)
    current_shareholder: list[SuperintendenciaShareholder] = Field(default_factory=list)


scrapper_schema = {
    "not_found": NotFound,
    "ant": Ant,
    "sri": Sri,
    "supa": Superintendencia,
    "senescyt": Senescyt,
    "fis_gen_estado": FiscaliaGeneral,
    "min_educacion": MinEducacion,
    "min_interior": MinInterior,
}

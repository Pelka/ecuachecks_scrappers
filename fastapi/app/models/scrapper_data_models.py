from pydantic import BaseModel, validator, Field
from datetime import datetime
from decimal import Decimal


class NotFoundDataModel(BaseModel):
    message: str


# --> Ant Data Models
class AntDataModel(BaseModel):
    full_name: str
    id_number: str
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


# --> Sri Data Models
class SriDataModel(BaseModel):
    full_name: str
    id_number: str
    message: str
    firm_debts: Decimal
    disputed_debts: Decimal
    payment_facilities: Decimal

    @validator("firm_debts", "disputed_debts", "payment_facilities", pre=True)
    def str_to_decimal(cls, value):
        return Decimal(value)


# --> Supa Data Models
class SupaDataModel(BaseModel):
    legal_representative: str
    primary_obligator: str
    province: str
    jurisdictional_depency: str
    card_code: str
    judicial_process: str
    type_alimony: str
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


# --> Senescyt Data Models
class SenescytDegreeModel(BaseModel):
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


class SenescytDataModel(BaseModel):
    id_number: str
    full_name: str
    gender: bool
    nacionality: str
    degress: list[SenescytDegreeModel] = Field(default_factory=list)

    @validator("gender", pre=True)
    def gender_to_bool(cls, value):
        return True if value == "MASCULINO " else False

    @validator("nacionality", pre=True)
    def upper_to_capitalize(cls, value):
        return value.capitalize()


# --> State AG Data Models
class PersonDataModel(BaseModel):
    id_number: str
    full_name: str
    status: str

    @validator("status", pre=True)
    def upper_to_capitalize(cls, value):
        return value.capitalize()


class StateAGDataModel(BaseModel):
    no_process: str
    place: str
    date: datetime
    state: str
    no_office: str
    crime: str
    unit: str
    attorney: str
    people: list[PersonDataModel] = Field(default_factory=list)

    @validator("date", pre=True)
    def date_to_datetime(cls, value):
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    @validator("attorney", pre=True)
    def split_attorney(cls, value):
        return value.split(": ")[1]

    @validator("place", "state", "unit", "attorney", pre=True)
    def upper_to_capitalize(cls, value):
        return " ".join([word.capitalize() for word in value.split(" ")])


# --> Min Educacion Data Models
class MinEducacionDataModel(BaseModel):
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


# --> Min Interior Data Models
class MinInteriorDataModel(BaseModel):
    full_name: str
    id_number: str
    doc_type: str
    background: bool
    certidicate: str

    @validator("background", pre=True)
    def background_to_bool(cls, value):
        return True if value == "SI" else False

    @validator("doc_type", pre=True)
    def upper_to_capitalize(cls, value):
        return " ".join([word.capitalize() for word in value.split(" ")])


DATA_MODELS = {
    "ant": AntDataModel,
    "sri": SriDataModel,
    "supa": SupaDataModel,
    "senescyt": SenescytDataModel,
    "fis_gen_estado": StateAGDataModel,
    "min_educacion": MinEducacionDataModel,
    "min_interior": MinInteriorDataModel,
}

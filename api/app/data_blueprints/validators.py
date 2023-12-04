from pydantic import BeforeValidator
from typing_extensions import Annotated

from datetime import datetime
from decimal import Decimal


class CleaningValidators:
    StrToInt = Annotated[int, BeforeValidator(lambda v: int(v))]
    StrToFloat = Annotated[float, BeforeValidator(lambda v: float(v))]
    StrToDecimal = Annotated[Decimal, BeforeValidator(lambda v: Decimal(v))]
    StrToCapitalize = Annotated[str, BeforeValidator(lambda v: v.capitalize())]
    MoneyToDecimal = Annotated[
        Decimal, BeforeValidator(lambda v: Decimal(v.replace("$", "")))
    ]
    GenderBool = Annotated[
        bool, BeforeValidator(lambda v: True if v == "MASCULINO" else False)
    ]
    CapitalizedPhrase = Annotated[
        str, BeforeValidator(lambda v: " ".join([w.capitalize() for w in v.split(" ")]))
    ]
    FormatedDate = Annotated[
        datetime, BeforeValidator(lambda v: datetime.strptime(v, "%Y-%m-%d"))
    ]
    FormatedDatetime = Annotated[
        datetime, BeforeValidator(lambda v: datetime.strptime(v, "%Y-%m-%d %H:%M:%S"))
    ]

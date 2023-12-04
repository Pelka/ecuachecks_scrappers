import re
from decimal import Decimal

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from sri.items import SriItem


# process fields
def process_fields(
    item_adapter: ItemAdapter, fields_key: list[str], func: any, *args, **kwargs
):
    for field_key in fields_key:
        value = item_adapter.get(field_key)
        if value is not None:
            item_adapter[field_key] = func(value, *args, **kwargs)


def string_to_decimal(
    value: str, non_numeric: bool = False, splited_by_comma: bool = False
):
    if splited_by_comma:
        splited_value = value.split(",")
        value = ".".join(splited_value)

    if non_numeric:
        value = re.findall(
            r"\d+\.\d+|\d+",
            value,
        )[0]

    decimal_value = Decimal(value)
    return str(decimal_value)


# data formating & cleaning functions
def strip_white_spaces(item_adapter: ItemAdapter):
    field_names = item_adapter.field_names()
    for field_name in field_names:
        value = item_adapter.get(field_name)
        if value is not None:
            item_adapter[field_name] = value.strip()


class PreprocesDataPipeline:
    def process_item(self, item, spider):
        if isinstance(item, SriItem):
            adapter = ItemAdapter(item)

            # Strip all white spaces from strings
            strip_white_spaces(adapter)

            # Firm Debts,  Disputed Debts --> decimal
            process_fields(
                item_adapter=adapter,
                fields_key=["firm_debts", "disputed_debts", "payment_facilities"],
                func=string_to_decimal,
                non_numeric=True,
            )

        return item

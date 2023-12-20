# usefull functions
import re
from datetime import datetime

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from ant.items import AntItem


# process fields
def process_fields(item_adapter: ItemAdapter, fields_key: list[str], func: any, *args, **kwargs):
    for field_key in fields_key:
        value = item_adapter.get(field_key)
        if value is not None:
            item_adapter[field_key] = func(value, *args, **kwargs)


def string_to_float(value: str, non_numeric: bool = False, splited_by_comma: bool = False):
    if splited_by_comma:
        splited_value = splited_value = value.split(",")
        value = ".".join(splited_value)

    if non_numeric:
        value = re.findall(r"\d+\.\d+|\d+", value)[0]

    float_value = float(value)
    return float_value


def string_to_timestamp(value: str, format_string: str):
    date_value = datetime.strptime(value, format_string)
    date_value = date_value.isoformat(sep=" ")
    return date_value


# data formating & cleaning functions
def strip_white_spaces(item_adapter: ItemAdapter):
    field_names = item_adapter.field_names()
    for field_name in field_names:
        value = item_adapter.get(field_name)
        if value is not None:
            item_adapter[field_name] = value.strip()


class PreprocesDataPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Strip all white spaces from strings
        strip_white_spaces(adapter)

        # Expedition & Expiration dates --> timestamp
        process_fields(
            item_adapter=adapter,
            fields_key=["expedition_date", "expiration_date"],
            func=string_to_timestamp,
            format_string="%d-%m-%Y",
        )

        # Points & Total --> float
        process_fields(
            item_adapter=adapter,
            fields_key=["points", "total"],
            func=string_to_float,
            splited_by_comma=True,
        )

        return item

import re
import json
from typing import List
from decimal import Decimal
from datetime import datetime

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

# process fields
def process_fields(item_adapter: ItemAdapter, fields_key: List[str], func: any, *args, **kwargs):
    for field_key in fields_key:
        value = item_adapter.get(field_key)
        if value is not None:
            item_adapter[field_key] = func(value, *args, **kwargs)


# data formating & cleaning functions
def strip_white_spaces(item_adapter: ItemAdapter):
    field_names = item_adapter.field_names()
    for field_name in field_names:
        value = item_adapter.get(field_name)
        if value is not None:
            item_adapter[field_name] = value.strip()


def capitalize_words(value):
    words = value.split()
    capitalized_words = [word.capitalize() if len(word) > 1 else word for word in words]
    value = ' '.join(capitalized_words)
    return value


def string_to_float(value: str, non_numeric: bool = False, splited_by_comma: bool = False):
    if splited_by_comma:
        splited_value = splited_value= value.split(",")
        value = ".".join(splited_value)
        
    if non_numeric:
            value = re.findall(r'\d+\.\d+|\d+', value)[0]
            
    float_value = float(value)
    return float_value
 
        
def string_to_datetime(value: str, format_string: str):
    date_value = datetime.strptime(value, format_string)
    date_value = datetime.strftime(date_value)
    return date_value


def string_to_decimal(value: str, non_numeric: bool = False, splited_by_comma: bool = False):
    if splited_by_comma:
        splited_value = value.split(",")
        value = ".".join(splited_value)
    
    if non_numeric:
        value = re.findall(r'\d+\.\d+|\d+', value)[0]
    
    decimal_value = Decimal(value)
    return decimal_value

            
# spiders pipelines
class DPPAntPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Strip all white spaces from strings
        strip_white_spaces(adapter)
        
        # Expedition & Expiration dates --> timestamp
        process_fields(
            item_adapter = adapter, 
            fields_key = ["expedition_date", "expiration_date"], 
            func = string_to_datetime, 
            format_string = "%d-%m-%Y"
        )
        
        # Points & Total --> float
        process_fields(
            item_adapter = adapter, 
            fields_key = ["points", "total"],
            func = string_to_float,
            splited_by_comma = True
        )
        
        return item

class DPPSriPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Strip all white spaces from strings
        strip_white_spaces(adapter)

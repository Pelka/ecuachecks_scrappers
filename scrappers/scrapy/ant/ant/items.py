from scrapy import Item, Field


# --- ANT item
class AntItem(Item):
    id_number = Field()
    full_name = Field()
    license_type = Field()
    expedition_date = Field()
    expiration_date = Field()
    points = Field()
    total = Field()

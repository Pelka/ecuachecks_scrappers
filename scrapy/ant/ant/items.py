from scrapy import Item, Field

# --- ANT item
class AntItem(Item):
    full_name = Field()
    cedula = Field()
    license_type = Field()
    expedition_date = Field()
    expiration_date = Field()
    points = Field()
    total = Field()
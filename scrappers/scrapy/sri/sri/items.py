from scrapy import Item, Field


# --- Sri item
class SriItem(Item):
    id_number = Field()
    full_name = Field()
    message = Field()
    firm_debts = Field()
    disputed_debts = Field()
    payment_facilities = Field()

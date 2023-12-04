from scrapy import Item, Field


class NotFoundItem(Item):
    message = Field()


# --- Sri item
class SriItem(Item):
    full_name = Field()
    cedula = Field()
    message = Field()
    firm_debts = Field()
    disputed_debts = Field()
    payment_facilities = Field()

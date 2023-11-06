# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

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


# --- Expel items
class ExpelCaseItem(Item):
    no_process = Field()
    entry_date = Field()
    matter = Field()
    action_type = Field()
    crime_issue = Field()
    parties_victims = Field()
    defendants_accused = Field()


class ExpelMovementItem(Item):
    no_movement = Field()
    entry_date = Field()
    jurisdiction = Field()
    city = Field()


class ExpelDetailItem(Item):
    entry_date = Field()
    detail = Field()
    article = Field()


# --- Ministerio Educacion item
class MinisterioEducacionItem(Item):
    no = Field()
    cedula = Field()
    full_name = Field()
    degree = Field()
    speciality = Field()
    graduation_date = Field()
    ref_number = Field()


# --- Senescyt item
class SenescytItem(Item):
    full_name = Field()
    cedula = Field()
    gender = Field()
    nationality = Field()
    degree = Field()
    college = Field()
    certificate_type = Field()
    recognized = Field()
    register_number = Field()
    register_date = Field()
    area = Field()
    note = Field()


# --- Sri item
class SriItem(Item):
    full_name = Field()
    cedula = Field()
    message = Field()
    firm_debts = Field()
    disputed_debts = Field()
    payment_facilities = Field()


# --- Supa item
class SupaItem(Item):
    card_number = Field()
    process_number = Field()
    jurisdiction = Field()
    process_type = Field()
    legal_representative = Field()
    demanded = Field()
    current_payment = Field()
from peewee import *

from .BaseModel import BaseModel


class PropertiesKeys:
    id: str = 'id'
    created_at: str = 'created_at'

    search_by_address: str = 'search_by_address'
    brt_number: str = 'brt_number'
    property_address: str = 'property_address'
    postal_code: str = 'postal_code'
    owner_name: str = 'owner_name'
    includes_payments_through: str = 'includes_payments_through'


Keys = PropertiesKeys


class Properties(BaseModel):
    global Keys

    search_by_address = TextField(null=True)
    brt_number = IntegerField(unique=True, null=True)
    property_address = TextField(null=True)
    postal_code = IntegerField(null=True)
    owner_name = CharField(max_length=1000, null=True)
    includes_payments_through = DateField(null=True)

    @staticmethod
    def initialize(params: dict) -> 'Properties':
        model = Properties()

        if Keys.id in params:
            model.id = params[Keys.id]

        if Keys.created_at in params:
            model.created_at = params[Keys.created_at]

        if Keys.search_by_address in params:
            model.search_by_address = params[Keys.search_by_address]

        if Keys.brt_number in params:
            model.brt_number = params[Keys.brt_number]

        if Keys.property_address in params:
            model.property_address = params[Keys.property_address]

        if Keys.postal_code in params:
            model.postal_code = params[Keys.postal_code]

        if Keys.owner_name in params:
            model.owner_name = params[Keys.owner_name]

        if Keys.includes_payments_through in params:
            model.includes_payments_through = params[Keys.includes_payments_through]

        return model

    def values(self):

        if self.brt_number == '':
            self.brt_number = None

        if self.postal_code == '':
            self.postal_code = None

        if self.includes_payments_through == '':
            self.includes_payments_through = None

        return [self.id, self.created_at, self.search_by_address, self.brt_number, self.property_address,
                self.postal_code, self.owner_name, self.includes_payments_through]

from peewee import *

from .BaseModel import BaseModel
from .Properties import Properties


class TaxesKeys:
    id: str = 'id'
    created_at: str = 'created_at'

    property_internal_id: str = 'property_internal_id'
    tax_category: str = 'tax_category'

    principal: str = 'principal'
    interest: str = 'interest'
    penalty: str = 'penalty'
    other: str = 'other'
    total: str = 'total'
    lien_number: str = 'lien_number'
    city_solicitor: str = 'city_solicitor'
    status: str = 'status'


Keys = TaxesKeys


class Taxes(BaseModel):
    global Keys

    property_internal_id = ForeignKeyField(Properties, backref='properties', on_update='CASCADE', on_delete='CASCADE')
    tax_category = CharField(max_length=512)

    principal = CharField(max_length=512, null=True)
    interest = CharField(max_length=512, null=True)
    penalty = CharField(max_length=512, null=True)
    other = CharField(max_length=512, null=True)
    total = CharField(max_length=512, null=True)
    lien_number = CharField(max_length=512, null=True)
    city_solicitor = TextField(null=True)
    status = CharField(max_length=1000, null=True)

    @staticmethod
    def initialize(params: dict) -> 'Taxes':
        model = Taxes()

        if Keys.id in params:
            model.id = params[Keys.id]

        if Keys.created_at in params:
            model.created_at = params[Keys.created_at]

        if Keys.property_internal_id in params:
            model.property_internal_id = params[Keys.property_internal_id]

        if Keys.tax_category in params:
            model.tax_category = params[Keys.tax_category]

        if Keys.principal in params:
            model.principal = params[Keys.principal]

        if Keys.interest in params:
            model.interest = params[Keys.interest]

        if Keys.penalty in params:
            model.penalty = params[Keys.penalty]

        if Keys.other in params:
            model.other = params[Keys.other]

        if Keys.total in params:
            model.total = params[Keys.total]

        if Keys.lien_number in params:
            model.lien_number = params[Keys.lien_number]

        if Keys.city_solicitor in params:
            model.city_solicitor = params[Keys.city_solicitor]

        if Keys.status in params:
            model.status = params[Keys.status]

        return model

    def values(self):

        try:
            property_id = self.property_internal_id.id
        except DoesNotExist:
            property_id = None

        return [self.id, self.created_at, property_id, self.tax_category, self.principal, self.interest,
                self.penalty, self.other, self.total, self.lien_number, self.city_solicitor, self.status]

    class Meta:
        global Keys

        indexes = (((Keys.property_internal_id, Keys.tax_category), True),)

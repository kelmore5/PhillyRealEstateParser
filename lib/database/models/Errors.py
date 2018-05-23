from peewee import *

from .BaseModel import BaseModel


class ErrorsKeys:
    id: str = 'id'
    created_at: str = 'created_at'

    search_by_address: str = 'search_by_address'
    error_code: str = 'error_code'
    message: str = 'message'


Keys = ErrorsKeys


class Errors(BaseModel):
    global Keys

    search_by_address = CharField(max_length=2500)
    error_code = CharField(max_length=512)
    message = TextField()

    @staticmethod
    def initialize(params: dict) -> 'Errors':
        model = Errors()

        if Keys.id in params:
            model.id = params[Keys.id]

        if Keys.created_at in params:
            model.created_at = params[Keys.created_at]

        if Keys.search_by_address in params:
            model.search_by_address = params[Keys.search_by_address]

        if Keys.error_code in params:
            model.brt_number = params[Keys.error_code]

        if Keys.message in params:
            model.property_address = params[Keys.message]

        return model

    def values(self):
        return [self.id, self.created_at, self.search_by_address, self.error_code, self.message]

    def to_dict(self):
        output = dict()

        output[Keys.id] = self.id
        output[Keys.created_at] = self.created_at
        output[Keys.search_by_address] = self.search_by_address
        output[Keys.error_code] = self.error_code
        output[Keys.message] = self.message

        return output

    class Meta:
        global Keys

        indexes = (((Keys.search_by_address, Keys.error_code), True),)

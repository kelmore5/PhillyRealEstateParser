import datetime
import os.path
import sys
from typing import Sequence

from peewee import *

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(os.path.join(dir_path, '../../..'))
sys.path.append(dir_path)

# noinspection PyPep8Naming,PyUnresolvedReferences
from lib.utils.lib.Jsons import Jsons as jsons

file_name: str = 'philly.db'

dir_path: str = ''
try:
    dir_path = os.path.dirname(os.path.realpath(__file__))
except NameError:
    dir_path = os.path.dirname(os.path.abspath(sys.argv[0]))

db_file_path: str = os.path.abspath(os.path.join(dir_path, './' + file_name))

db: SqliteDatabase = SqliteDatabase(db_file_path, pragmas=(('foreign_keys', 'on'),))


class BaseModelKeys:
    id = 'id'
    created_at = 'created_at'


class BaseModel(Model):
    db = db
    id = AutoField()
    created_at = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return str(jsons.create_dict(self._meta.sorted_field_names, self.values()))

    def __repr__(self):
        return str(jsons.create_dict(self._meta.sorted_field_names, self.values()))

    # noinspection PyProtectedMember
    def to_dict(self):
        output = dict()

        keys = self._meta.sorted_field_names
        values = self.values()

        # print(keys)
        # print(values)

        if len(keys) != len(values):
            raise IndexError('The length of keys and values were not equal for {} class. '
                             'This needs to be fixed internally'.format(self._meta.name))

        for idx in range(len(values)):
            value = values[idx]
            if value is not None:
                output[keys[idx]] = value

        return output

    def values(self):
        return [self.created_at]

    def upload_many(self, upload: Sequence['BaseModel']):
        # self.insert_many(temp).on_conflict_replace().execute()

        # TODO: Rewrite so more concise like above
        # Problem: insert_many only uses first dictionary reference for keys to update in database,
        # rather than looking at each item individually
        # Going to have to write custom SQL queries like in Bookshelf.......
        for x in upload:
            self.insert(x.to_dict()).on_conflict_replace().execute()

    class Meta:
        database = db

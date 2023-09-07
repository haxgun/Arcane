from typing import List

from arcane import settings

from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, PrimaryKeyField

db = SqliteDatabase(settings.DB_NAME)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)
    name = CharField(unique=True, null=False)

    class Meta:
        order_by = id
        database = db


class Channel(BaseModel):
    class Meta:
        db_table = 'channels'

    @staticmethod
    def get_all_channel_names() -> List[str]:
        return [channel.name for channel in Channel.select()]


class Command(BaseModel):
    response = CharField(default="Нет ответа")
    channel = ForeignKeyField(Channel, backref='commands', on_delete='CASCADE')

    class Meta:
        db_table = 'commands'


class Alias(BaseModel):
    command = ForeignKeyField(Command, backref='aliases', on_delete='CASCADE')
    channel = ForeignKeyField(Channel, backref='aliases', on_delete='CASCADE')

    class Meta:
        db_table = 'aliases'


db.create_tables([Channel, Command, Alias])

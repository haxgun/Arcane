from typing import List

from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, PrimaryKeyField, IntegerField

from arcane import settings
from arcane.settings import PREFIX

db = SqliteDatabase(settings.DB_NAME)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)
    name = CharField(unique=True, null=False)

    class Meta:
        order_by = id
        database = db


class Channel(BaseModel):
    oauth = CharField(null=True)
    cliend_id = CharField(null=True)
    prefix = CharField(default=PREFIX, max_length=1)
    valorant = CharField(null=True)

    class Meta:
        db_table = 'channels'

    @staticmethod
    def get_all_channel_names() -> List[str]:
        return [channel.name for channel in Channel.select()]


class Command(BaseModel):
    response = CharField(default="Нет ответа")
    channel = ForeignKeyField(Channel, backref='commands', on_delete='CASCADE')
    cooldown = IntegerField(default=15)

    class Meta:
        db_table = 'commands'


class Alias(BaseModel):
    command = ForeignKeyField(Command, backref='aliases', on_delete='CASCADE')
    channel = ForeignKeyField(Channel, backref='aliases', on_delete='CASCADE')

    class Meta:
        db_table = 'aliases'


db.create_tables([Channel, Command, Alias])

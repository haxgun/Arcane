from typing import List

from haxbod import settings

from peewee import SqliteDatabase, Model, CharField, IntegerField, ForeignKeyField, DoesNotExist

db = SqliteDatabase(settings.DB_NAME)


class Channel(Model):
    name = CharField(null=False, unique=True)

    class Meta:
        database = db

    @staticmethod
    def get_all_channel_names() -> List[str]:
        return [channel.name for channel in Channel.select()]


class Command(Model):
    id = IntegerField(unique=True, primary_key=True, null=False)
    name = CharField(unique=True, null=False)
    response = CharField(default="Нет ответа")
    channel = ForeignKeyField(Channel, backref='commands', on_delete='CASCADE')

    class Meta:
        database = db


class Alias(Model):
    name = CharField(unique=True, null=False)
    command = ForeignKeyField(Command, backref='aliases', on_delete='CASCADE')

    class Meta:
        database = db


db.create_tables([Channel, Command, Alias])

from typing import List

from peewee import SqliteDatabase, Model, CharField, PrimaryKeyField, BooleanField

from arcane import settings

db = SqliteDatabase(settings.DB_NAME)


class BaseModel(Model):
    id = PrimaryKeyField(unique=True)
    name = CharField(unique=True, null=False)

    class Meta:
        order_by = id
        database = db


class Channel(BaseModel):
    riot_id = CharField(null=True)
    otherplayer = BooleanField(default=False)

    class Meta:
        db_table = 'channels'

    @staticmethod
    def get_all_channel_names() -> List[str]:
        return [channel.name for channel in Channel.select()]


db.create_tables([Channel])

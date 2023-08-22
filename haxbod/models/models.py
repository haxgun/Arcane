from typing import List

from pony.orm import Database
from pony.orm.core import PrimaryKey, Required, db_session, Set

from haxbod import settings

db = Database()
db.bind(provider='sqlite', filename=f'{settings.BASE_DIR}/{settings.DB_NAME}', create_db=True)


class Channel(db.Entity):
    name = Required(str, unique=True)
    commands = Set('Command', cascade_delete=False)

    @staticmethod
    @db_session
    def get_all_channel_names() -> List[str]:
        return [channel.name for channel in Channel.select()]


class Command(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    response = Required(str, default="Нет ответа")
    channel = Required(Channel)


db.generate_mapping(create_tables=True)

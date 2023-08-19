from pony.orm.core import PrimaryKey, Required, db_session, Set
from pony.orm import Database
from haxbod import config

db = Database()
db.bind(provider='sqlite', filename=f'{config.BASE_DIR}/{config.DB_NAME}', create_db=True)


class Channel(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    commands = Set('Command', cascade_delete=False)

    @staticmethod
    def get_all_channel_names():
        with db_session:
            return [channel.name for channel in Channel.select()]


class Command(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    response = Required(str, default="Нет ответа")
    channel = Required(Channel)


db.generate_mapping(create_tables=True)

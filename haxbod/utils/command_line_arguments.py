from pony.orm import db_session
from haxbod.bot import Haxbod
from haxbod.models import db
from haxbod.utils.twitchapi import existing_channel_twitch
from haxbod.utils.print import print_success, print_error, input_answer

bot = Haxbod()


def add_channel() -> None:
    channel_name = str(input_answer('Which channel do you want to add?'))

    if not existing_channel_twitch(channel_name):
        print_error('There is no such user!')
        return

    with db_session:
        existing_channel_db = db.Channel.get(name=channel_name)

        if not existing_channel_db:
            channel = db.Channel(name=channel_name)
            print_success(f'User @{channel_name} added.')
        else:
            print_error(f'User @{channel_name} already exists.')


def run_bot() -> None:
    bot.run()


def remove_channel() -> None:
    channel_name = str(input_answer('Which channel do you want to add?'))

    with db_session:
        existing_channel = db.Channel.get(name=channel_name)

        if existing_channel:
            existing_channel.delete()
            print_success(f'User @{channel_name} has been removed from the database.')
        else:
            print_error(f'User @{channel_name} is not in the database.')
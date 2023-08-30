from haxbod.bot import Haxbod
from haxbod.models import Channel
from haxbod.utils.twitchapi import existing_channel_twitch
from haxbod.utils.print import print_success, print_error, input_answer

bot = Haxbod()


def add_channel() -> None:
    channel_name = str(input_answer('Which channel do you want to add?'))

    if not existing_channel_twitch(channel_name):
        print_error('There is no such user!')
        return

    try:
        existing_channel_db = Channel.get(Channel.name == channel_name)
        print_error(f'User @{channel_name} already exists.')
    except Exception:
        channel = Channel.create(name=channel_name)
        print_success(f'User @{channel_name} added.')


def remove_channel() -> None:
    channel_name = str(input_answer('Which channel do you want to add?'))

    existing_channel = Channel.get(Channel.name == channel_name)

    if existing_channel:
        existing_channel.delete_instance()
        existing_channel.save()
        print_success(f'User @{channel_name} has been removed from the database.')
    else:
        print_error(f'User @{channel_name} is not in the database.')


def run_bot() -> None:
    bot.run()


from arcane import bot
from arcane.models import Channel
from arcane.modules import printt
from arcane.modules.api.twitch import existing_channel_twitch


def add_channel() -> None:
    channel_name = str(printt.input_answer('Which channel do you want to add?'))

    if not existing_channel_twitch(channel_name):
        printt.error('There is no such user!')
        return

    try:
        existing_channel_db = Channel.get(Channel.name == channel_name)
        printt.error(f'User @{channel_name} already exists.')
    except Exception:
        channel = Channel.create(name=channel_name)
        printt.success(f'User @{channel_name} added.')


def remove_channel() -> None:
    channel_name = str(printt.input_answer('Which channel do you want to add?'))

    existing_channel = Channel.get(Channel.name == channel_name)

    if existing_channel:
        existing_channel.delete_instance()
        existing_channel.save()
        printt.success(f'User @{channel_name} has been removed from the database.')
    else:
        printt.error(f'User @{channel_name} is not in the database.')


def run_bot() -> None:
    bot.run()

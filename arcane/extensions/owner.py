from peewee import IntegrityError, DoesNotExist

from arcane import bot
from arcane.models import Channel
from arcane.modules.api.twitch import api_latency, existing_channel_twitch


@bot.command(name='channels', aliases=['ch'], permissions=['owner'], hidden=True)
async def cmd_channels(msg, subcommands: str = None) -> None:
    channels = Channel.get_all_channel_names()
    await msg.reply(f'Channels: {", ".join(channels)}')


@cmd_channels.subcommand(name='add', aliases=['a'], permissions=['owner'])
async def cmd_add_channel(msg, channel_name: str) -> None:
    if channel_name.startswith('@'):
        channel_name = channel_name.lstrip("@")

    channel_name = channel_name.lower()

    if not existing_channel_twitch(channel_name):
        await msg.reply('There is no such user!')
        return
    try:
        channel = Channel.create(name=channel_name)
        await bot.join_channel(channel_name)
        await msg.reply(f'The user @{channel_name} added.')
    except IntegrityError:
        await msg.reply(f'The user @{channel_name} already exists.')


@cmd_channels.subcommand(name='remove', aliases=['rm'], permissions=['owner'])
async def cmd_del_channel(msg, channel_name: str) -> None:
    if channel_name.startswith('@'):
        channel_name = channel_name.lstrip("@")

    channel_name = channel_name.lower()

    try:
        channel = Channel.get(Channel.name == channel_name)
        channel.delete_instance()
        channel.save()
        await bot.part_channel(channel_name)
        await msg.reply(f'The user @{channel_name} has been removed from the database.')
    except DoesNotExist:
        await msg.reply(f'The user @{channel_name} is not in the database.')


@bot.command(name='bot', permissions=['owner'], hidden=True)
async def cmd_bot_info(msg) -> None:
    api_latency_ms = await api_latency()

    if api_latency_ms:
        await msg.reply(f'⚡ Bot online! 🏓 API {api_latency_ms}ms')
    else:
        await msg.reply(f'⚡ Bot online!')

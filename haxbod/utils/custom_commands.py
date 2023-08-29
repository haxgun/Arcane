from peewee import DoesNotExist
from twitchio.ext import commands

import emoji

from haxbod.models import Channel, Command


def starts_with_emoji(text):
    if emoji.demojize(text) != text:
        return True
    return False


async def find_custom_command(ctx: commands.Context) -> bool:
    command_name = ctx.message.content.split()[0][1:]

    if starts_with_emoji(command_name):
        return False

    try:
        channel = Channel.get(Channel.name == ctx.channel.name)
        command = Command.get(Command.name == command_name, Command.channel == channel)
        return True
    except DoesNotExist:
        return False


async def custom_command_response(ctx: commands.Context) -> str:
    command_name = ctx.message.content.split()[0][1:]

    channel = Channel.get(Channel.name == ctx.channel.name)
    command = Command.get(Command.name == command_name, Command.channel == channel)

    return command.response


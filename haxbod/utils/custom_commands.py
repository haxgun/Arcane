from pony.orm import db_session
from twitchio.ext import commands

from haxbod.models import db

import emoji


def starts_with_emoji(text):
    if emoji.demojize(text) != text:
        return True
    return False


async def find_custom_command(ctx: commands.Context) -> bool:
    command_name = ctx.message.content.split()[0][1:]

    if starts_with_emoji(command_name):
        return False

    with db_session:
        channel = db.Channel.get(name=ctx.channel.name)
        command = db.Command.get(name=command_name, channel=channel.id)

        if command:
            return True
        else:
            return False


async def custom_command_response(ctx: commands.Context) -> str:
    command_name = ctx.message.content.split()[0][1:]

    with db_session:
        channel = db.Channel.get(name=ctx.channel.name)
        command = db.Command.get(name=command_name, channel=channel.id)

    return command.response


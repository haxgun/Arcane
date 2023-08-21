from pony.orm import db_session
from twitchio.ext.commands import Context

from haxbod.models import db


async def find_custom_command(ctx: Context) -> bool:
    command_name = ctx.message.content.split()[0][1:]

    with db_session:
        channel = db.Channel.get(name=ctx.channel.name)
        command = db.Command.get(name=command_name, channel=channel.id)

        if command:
            return True
        else:
            return False


async def custom_command_response(ctx: Context) -> str:
    command_name = ctx.message.content.split()[0][1:]

    with db_session:
        channel = db.Channel.get(name=ctx.channel.name)
        command = db.Command.get(name=command_name, channel=channel.id)

    return command.response


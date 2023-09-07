from peewee import DoesNotExist
from twitchio.ext import commands
import emoji
from arcane.models import Channel, Command, Alias


def starts_with_emoji(text):
    return emoji.demojize(text) != text


async def find_entity(ctx: commands.Context, EntityModel) -> bool:
    entity_name = ctx.message.content.split()[0][1:]

    if starts_with_emoji(entity_name):
        return False

    try:
        channel = Channel.get(Channel.name == ctx.channel.name)
        entity = EntityModel.get(EntityModel.name == entity_name, EntityModel.channel == channel)
        return True
    except DoesNotExist:
        return False


async def custom_command_response(ctx: commands.Context) -> str:
    command_name = ctx.message.content.split()[0][1:]
    channel = Channel.get(Channel.name == ctx.channel.name)
    command = Command.get(Command.name == command_name, Command.channel == channel)
    return command.response


async def alias_response(ctx: commands.Context) -> str:
    alias_name = ctx.message.content.split()[0][1:]
    channel = Channel.get(Channel.name == ctx.channel.name)
    alias = Alias.get(Alias.name == alias_name, Alias.channel == channel)
    command = alias.command
    return command.response

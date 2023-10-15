import emoji
from peewee import DoesNotExist

from arcane.models import Channel, Command, Alias
from arcane.modules.cooldowns import command_cooldown_manager
from arcane.modules.dataclasses import Message


def starts_with_emoji(text) -> bool:
    return emoji.demojize(text) != text


async def find_entity(msg: Message, entity) -> bool:
    entity_name = msg.content.split()[0][1:]

    if starts_with_emoji(entity_name):
        return False

    try:
        channel = Channel.get(Channel.name == msg.channel.name)
        entity_obg = entity.get(entity.name == entity_name, entity.channel == channel)
        return True
    except DoesNotExist:
        return False


async def get_command_data(msg: Message, EntityModel) -> tuple:
    command_name = msg.content.split()[0][1:]
    channel = Channel.get(Channel.name == msg.channel.name)
    entity = EntityModel.get(EntityModel.name == command_name, EntityModel.channel == channel)
    cooldown = entity.cooldown
    response = entity.response
    return command_name, cooldown, response


async def handle_custom_commands(msg: Message) -> None:
    count = 1
    command_name, response, cooldown = None, None, None
    channel = msg.channel.name

    if msg.author.is_broadcaster or msg.author.is_moderator:
        if len(msg.content.split()) > 1:
            try:
                count = int(msg.content.split()[1])
            except ValueError:
                pass

    if await find_entity(msg, Command):
        command_name, cooldown, response = await get_command_data(msg, Command)
    elif await find_entity(msg, Alias):
        command_name, cooldown, response = await get_command_data(msg, Alias)

    if response and cooldown:
        if command_cooldown_manager.can_use_command(channel, command_name, cooldown):
            command_cooldown_manager.update_command_cooldown(channel, command_name)
            for _ in range(count):
                await msg.send(response) if count > 1 else await msg.reply(response)

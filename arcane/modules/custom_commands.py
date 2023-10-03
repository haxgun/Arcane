import time

import emoji
from peewee import DoesNotExist

from arcane.models import Channel, Command, Alias
from arcane.modules.dataclasses import Message

cooldowns = {}


def starts_with_emoji(text) -> bool:
    return emoji.demojize(text) != text


async def find_entity(msg: Message, EntityModel) -> bool:
    entity_name = msg.content.split()[0][1:]

    if starts_with_emoji(entity_name):
        return False

    try:
        channel = Channel.get(Channel.name == msg.channel)
        entity = EntityModel.get(EntityModel.name == entity_name, EntityModel.channel == channel)
        return True
    except DoesNotExist:
        return False


async def custom_command_response(msg: Message) -> str:
    command_name = msg.content.split()[0][1:]
    channel = Channel.get(Channel.name == msg.channel)
    command = Command.get(Command.name == command_name, Command.channel == channel)
    return command.response


async def alias_response(msg: Message) -> str:
    alias_name = msg.content.split()[0][1:]
    channel = Channel.get(Channel.name == msg.channel)
    alias = Alias.get(Alias.name == alias_name, Alias.channel == channel)
    command = alias.command
    return command.response


async def can_use_command(user_id: str, command: str, cooldown_duration: int) -> bool:
    key = f'{user_id}:{command}'

    if key in cooldowns:
        last_used_time = cooldowns[key]
        current_time = time.time()
        if current_time - last_used_time < cooldown_duration:
            return False
    return True


async def update_command_cooldown(user_id: str, command: str) -> None:
    key = f'{user_id}:{command}'
    cooldowns[key] = time.time()


async def handle_custom_commands(msg: Message) -> None:
    entity = None
    response = None
    count = 1

    if msg.author.is_broadcaster or msg.author.is_moderator:
        if len(msg.content.split()) > 1:
            try:
                count = int(msg.content.split()[1])
            except ValueError:
                pass

    if await find_entity(msg, Command):
        entity = Command
        response = await custom_command_response(msg)
    elif await find_entity(msg, Alias):
        entity = Alias
        response = await alias_response(msg)

    if entity and response:
        user_id = msg.author.id
        command = msg.content.split()[0][1:]
        cooldown_duration = 5
        if await can_use_command(user_id, command, cooldown_duration):
            await update_command_cooldown(user_id, command)
            for _ in range(count):
                await msg.send(response) if count > 1 else await msg.reply(response)

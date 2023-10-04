import time

import emoji
from peewee import DoesNotExist

from arcane.models import Channel, Command, Alias
from arcane.modules.dataclasses import Message


class CommandCooldown:
    def __init__(self):
        self.cooldowns = {}

    def can_use_command(self, user_id, command, cooldown_duration):
        key = f'{user_id}:{command}'
        if key in self.cooldowns:
            last_used_time = self.cooldowns[key]
            current_time = time.time()
            if current_time - last_used_time < cooldown_duration:
                return False
        return True

    def update_command_cooldown(self, user_id, command):
        key = f'{user_id}:{command}'
        self.cooldowns[key] = time.time()


command_cooldown_manager = CommandCooldown()


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


async def get_command_data(msg: Message, EntityModel) -> tuple:
    command_name = msg.content.split()[0][1:]
    channel = Channel.get(Channel.name == msg.channel)
    entity = EntityModel.get(EntityModel.name == command_name, EntityModel.channel == channel)
    cooldown = entity.cooldown
    response = entity.response
    return command_name, cooldown, response


async def handle_custom_commands(msg: Message) -> None:
    count = 1
    command_name, response, cooldown = None, None, None

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
        user_id = msg.author.id

        if command_cooldown_manager.can_use_command(user_id, command_name, cooldown):
            command_cooldown_manager.update_command_cooldown(user_id, command_name)
            for _ in range(count):
                await msg.send(response) if count > 1 else await msg.reply(response)

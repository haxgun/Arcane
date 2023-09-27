import time

import emoji
from peewee import DoesNotExist

from arcane.models import Channel, Command, Alias

cooldowns = {}


def starts_with_emoji(text) -> bool:
    return emoji.demojize(text) != text


async def find_entity(ctx, EntityModel) -> bool:
    entity_name = ctx.message.content.split()[0][1:]

    if starts_with_emoji(entity_name):
        return False

    try:
        channel = Channel.get(Channel.name == ctx.channel.name)
        entity = EntityModel.get(EntityModel.name == entity_name, EntityModel.channel == channel)
        return True
    except DoesNotExist:
        return False


async def custom_command_response(ctx) -> str:
    command_name = ctx.message.content.split()[0][1:]
    channel = Channel.get(Channel.name == ctx.channel.name)
    command = Command.get(Command.name == command_name, Command.channel == channel)
    return command.response


async def alias_response(ctx) -> str:
    alias_name = ctx.message.content.split()[0][1:]
    channel = Channel.get(Channel.name == ctx.channel.name)
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


async def handle_custom_commands(context) -> None:
    entity = None
    response = None
    count = 1

    if context.author.is_broadcaster or context.author.is_mod:
        if len(context.message.content.split()) > 1:
            try:
                count = int(context.message.content.split()[1])
            except ValueError:
                pass

    if await find_entity(context, Command):
        entity = Command
        response = await custom_command_response(context)
    elif await find_entity(context, Alias):
        entity = Alias
        response = await alias_response(context)

    if entity and response:
        user_id = context.message.author.id
        command = context.message.content.split()[0][1:]
        cooldown_duration = 5
        if await can_use_command(user_id, command, cooldown_duration):
            await update_command_cooldown(user_id, command)
            for _ in range(count):
                await context.send(response) if count > 1 else await context.reply(response)

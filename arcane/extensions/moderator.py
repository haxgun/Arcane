from peewee import DoesNotExist

from arcane import bot
from arcane.models import Channel, Command, Alias
from arcane.modules.custom_commands import starts_with_emoji
from arcane.modules.dataclasses import Message


async def send_usage_for_custom_commands(msg: Message) -> None:
    main_command = msg.content.split()[0]
    sub_command = msg.content.split()[1]
    await msg.reply(f'Usage: {main_command} {sub_command} <command> <response>')


@bot.command(name='me', permissions=['moderator', 'broadcaster'])
async def cmd_me(msg: Message, response: str = None) -> None:
    if not response:
        await msg.send('Usage: !me <response>')
        return
    await msg.me(response)


@bot.command(name='spam', aliases=['sm', 'спам'], permissions=['moderator', 'broadcaster'], cooldown=0)
async def cmd_spam(msg: Message, count: int = None, response: str = None) -> None:
    if not count or not response:
        await bot.say(msg.channel, 'Usage: !spam <count> <response>')
        return
    max_count = 20
    if count < max_count:
        for _ in range(count):
            await msg.send(response)
    else:
        await msg.reply(f'Error! Count must be less than {max_count}!')


@bot.command(name='commands', aliases=['cmds'])
async def cmd_commands(msg: Message, subcommand: str = None) -> None:
    bot_commands = list(bot.commands.keys())

    channel = Channel.get(Channel.name == msg.channel.name)
    custom_commands = Command.select().where(Command.channel == channel)

    if custom_commands:
        all_commands = bot_commands + [custom_command.name for custom_command in custom_commands]
    else:
        all_commands = bot_commands

    commands_str = ', '.join(sorted(all_commands))

    if commands_str:
        await msg.reply(f'Commands: {commands_str}')
    else:
        await msg.reply(f'No commands.')


@cmd_commands.subcommand(name='add', aliases=['a'], permissions=['moderator', 'broadcaster'], cooldown=0)
async def cmd_add_command(msg: Message, command_name: str = None, response: str = None) -> None:
    if starts_with_emoji(command_name):
        await msg.reply('❌ Command must not contain an emoji!')
        return
    channel = Channel.get(Channel.name == msg.channel.name)
    command = Command.get_or_none(Command.name == command_name, Command.channel == channel)
    if not command:
        command = Command.create(
            name=command_name,
            response=response,
            channel=channel
        )
        await msg.reply(f'✅ !{command_name}')
    else:
        await msg.reply(f'❌ !{command_name} already exists.')


@cmd_commands.subcommand(name='remove', aliases=['rm'], permissions=['moderator', 'broadcaster'], cooldown=0)
async def cmd_remove_command(msg: Message, command_name: str = None) -> None:
    channel = Channel.get(Channel.name == msg.channel.name)
    command = Command.get_or_none(Command.name == command_name, Command.channel == channel)

    if command:
        command.delete_instance()
        command.save()
        await msg.reply('✅')
    else:
        await msg.reply('❌')


@cmd_commands.subcommand(name='edit', aliases=['e'], permissions=['moderator', 'broadcaster'], cooldown=0)
async def cmd_edit_command(msg: Message, command_name: str = None, response: str = None) -> None:
    channel = Channel.get(Channel.name == msg.channel.name)
    command = Command.get_or_none(Command.name == command_name, Command.channel == channel)
    if command:
        command.response = response
        command.save()
        await msg.reply(f'✅ !{command_name}')
    else:
        await msg.reply('❌')


@bot.command(name='aliases', aliases=['als'])
async def cmd_aliases(msg: Message, subcommand: str = None) -> None:
    channel = Channel.get(Channel.name == msg.channel.name)
    aliases = Alias.select().join(Command).where(Command.channel == channel)
    if aliases:
        aliases_str = ', '.join([alias.name for alias in aliases])
        await msg.reply(f'Aliases: {aliases_str}')
    else:
        await msg.reply(f'No aliases.')


@cmd_aliases.subcommand(name='add', aliases=['a'], permissions=['moderator', 'broadcaster'], cooldown=0)
async def cmd_add_alias(msg: Message, command_name: str = None, alias_name: str = None) -> None:
    if not command_name or not alias_name:
        await send_usage_for_custom_commands(msg)
        return

    if starts_with_emoji(command_name):
        await msg.reply(f'Command must not contain an emoji!')
        return
    channel = Channel.get(name=msg.channel.name)
    command = Command.get_or_none(name=command_name, channel=channel)
    if command:
        alias = Alias.get_or_none(name=alias_name, channel=channel)
        if alias:
            await msg.reply(f'❌ !{alias_name} already exists.')
        else:
            Alias.create(name=alias_name, command=command, channel=channel)
            await msg.reply(f'✅ !{alias_name}')
        return
    await msg.reply('❌')


@cmd_aliases.subcommand(name='remove', aliases=['rm'], permissions=['moderator', 'broadcaster'], cooldown=0)
async def cmd_remove_alias(msg: Message, alias_name: str = None) -> None:
    if not alias_name:
        await send_usage_for_custom_commands(msg)
        return

    channel = Channel.get(name=msg.channel.name)
    alias = Alias.get_or_none(name=alias_name, channel=channel)
    if alias:
        alias.delete_instance()
        await msg.reply('✅')
    else:
        await msg.reply('❌')


@cmd_aliases.subcommand(name='edit', aliases=['e'], permissions=['moderator', 'broadcaster'], cooldown=0)
async def cmd_edit_alias(msg: Message, alias_name: str = None, new_name: str = None) -> None:
    if not alias_name or not new_name:
        await send_usage_for_custom_commands(msg)
        return
    try:
        channel = Channel.get(Channel.name == msg.channel.name)
        alias = Alias.get(Alias.name == alias_name, Alias.channel == channel)
        alias.name = new_name
        alias.save()
        await msg.reply(f'✅ !{new_name}')
    except DoesNotExist as e:
        print(e)
        await msg.reply('❌')


@bot.command(name='settings', aliases=['set'], permissions=['moderator', 'broadcaster'], cooldown=0)
async def cmd_settings(msg: Message, subcommand: str = None) -> None:
    pass


@cmd_settings.subcommand(name='valorant', aliases=['vlr'], permissions=['moderator', 'broadcaster'], cooldown=0)
async def cmd_settings_valorant(msg: Message, name_with_tag: str) -> None:
    if '#' in name_with_tag:
        channel = Channel.get(Channel.name == msg.channel.name)
        channel.valorant = name_with_tag
        channel.save()
        await msg.reply('✅')
    else:
        await msg.reply('❌')

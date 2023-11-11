from arcane import bot
from arcane.models import Channel
from arcane.dataclasses import Message


async def send_usage_for_custom_commands(msg: Message) -> None:
    main_command = msg.content.split()[0]
    sub_command = msg.content.split()[1]
    await msg.reply(f'Usage: {main_command} {sub_command} <command> <response>')


@bot.command(name='commands', aliases=['cmds'])
async def cmd_commands(msg: Message, subcommand: str = None) -> None:
    bot_commands = list(bot.commands.keys())
    all_commands = bot_commands
    commands_str = ', '.join(sorted(all_commands))

    if commands_str:
        await msg.reply(f'Commands: {commands_str}')
    else:
        await msg.reply(f'No commands.')


@bot.command(name='settings', aliases=['set'], permissions=['moderator', 'broadcaster', 'owner'], cooldown=0)
async def cmd_settings(msg: Message, subcommand: str = None) -> None:
    pass


@cmd_settings.subcommand(name='riotid', aliases=['id'], permissions=['moderator', 'broadcaster', 'owner'], cooldown=0)
async def cmd_settings_riotid(msg: Message, name_with_tag: str) -> None:
    if '#' in name_with_tag:
        channel = Channel.get(Channel.name == msg.channel.name)
        channel.riot_id = name_with_tag
        channel.save()
        await msg.reply('✅')
    else:
        await msg.reply('❌')


@cmd_settings.subcommand(name='otherplayer', aliases=['op'], permissions=['moderator', 'broadcaster', 'owner'], cooldown=0)
async def cmd_settings_otherplayer(msg: Message, argument: str = 'false') -> None:
    argument = argument.lower()
    if argument not in ['true', 'false']:
        await msg.reply('❌')
    else:
        channel = Channel.get(Channel.name == msg.channel.name)
        channel.otherplayer = argument == 'true'
        channel.save()
        await msg.reply('✅')

from arcane import bot
from arcane.models import Channel
from arcane.modules.api.valorant import get_rank_with_rr_and_elo, get_stats_last_game
from arcane.modules.dataclasses import Message


@bot.command(name='rank')
async def cmd_valorant_rank(msg: Message, valorant_name: str = None) -> None:
    if not valorant_name or '#' not in valorant_name:
        channel = Channel.get(Channel.name == msg.channel)
        valorant_name = channel.valorant
    info = await get_rank_with_rr_and_elo(valorant_name)
    if info:
        await msg.reply(info)
    else:
        await msg.reply('ERROR')


@bot.command(name='lastgame', aliases=['lg'])
async def cmd_valorant_lg(msg: Message) -> None:
    channel = Channel.get(Channel.name == msg.channel)
    valorant_name = channel.valorant
    info = await get_stats_last_game(valorant_name)
    if info:
        await msg.reply(info)
    else:
        await msg.reply('ERROR')

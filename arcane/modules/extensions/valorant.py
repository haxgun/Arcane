from arcane import bot
from arcane.models import Channel
from arcane.modules.dataclasses import Message
from arcane.modules.api.valorant import get_rank_with_rr_and_elo, get_stats_last_game


@bot.command(name='rank')
async def cmd_rank(msg: Message) -> None:
    channel = Channel.get(Channel.name == msg.channel)
    valorant_name = channel.valorant
    info = await get_rank_with_rr_and_elo(valorant_name)
    if info:
        await msg.reply(info)
    else:
        await msg.reply('ERROR')

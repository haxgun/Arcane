from arcane import bot
from arcane.models import Channel
from arcane.modules.api.valorant import get_rank_with_rr_and_elo, get_stats_last_game, get_win_lose
from arcane.dataclasses import Message


@bot.command(name='tracker', aliases=['profile'])
async def cmd_valorant_tracker(msg: Message, valorant_name: str = None) -> None:
    channel = Channel.get(Channel.name == msg.channel.name)
    if not valorant_name or '#' not in valorant_name or channel.riot_id:
        valorant_name = channel.valorant
    if valorant_name:
        name, tag = valorant_name.split('#')
        name = name.replace(' ', '%20')
        await msg.reply(f'Tracker - https://tracker.gg/valorant/profile/riot/{name}%23{tag}')


@bot.command(name='rank')
async def cmd_valorant_rank(msg: Message, valorant_name: str = None) -> None:
    channel = Channel.get(Channel.name == msg.channel.name)
    if not valorant_name or '#' not in valorant_name or channel.riot_id:
        valorant_name = channel.valorant
    if valorant_name:
        info = await get_rank_with_rr_and_elo(valorant_name)
        if info:
            await msg.reply(info)
        else:
            await msg.reply('❌')


@bot.command(name='lastgame', aliases=['lg'])
async def cmd_valorant_lg(msg: Message, valorant_name: str = None) -> None:
    channel = Channel.get(Channel.name == msg.channel.name)
    if not valorant_name or '#' not in valorant_name or channel.riot_id:
        valorant_name = channel.valorant
    if valorant_name:
        info = await get_stats_last_game(valorant_name)
        if info:
            await msg.reply(f'{info["map_name"]} ({info["win_status"]}: {info["red_score"]}/{info["blue_score"]}) - '
                            f'{info["character"]} - {info["kills"]}/{info["deaths"]}/{info["assists"]} - '
                            f'KD: {info["kdr"]} HS%: {info["hs"]} ADR: {info["adr"]}')
        else:
            await msg.reply('❌')


@bot.command(name='winlose', aliases=['wl'])
async def cmd_valorant_winlose(msg: Message, valorant_name: str = None) -> None:
    channel = Channel.get(Channel.name == msg.channel.name)
    if not valorant_name or '#' not in valorant_name or channel.riot_id:
        valorant_name = channel.valorant

    win_count, lose_count = await get_win_lose(valorant_name)
    if win_count + lose_count != 0:
        win_rate = round((win_count / (win_count + lose_count)) * 100)
    else:
        win_rate = 0
    await msg.reply(f'W: {win_count} L: {lose_count} ({win_rate}%)')

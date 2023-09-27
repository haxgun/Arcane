from arcane import bot
from arcane.modules.api.twitch import get_stream_title, set_stream_title, change_stream_game, get_game
from arcane.modules.dataclasses import Message


@bot.command(name='title', permissions=['moderador', 'broadcaster'])
async def cmd_title(msg: Message, title: str = None) -> None:
    old_title = await get_stream_title(channel_name=msg.channel)
    if len(title) > 3:
        if title == old_title:
            await msg.reply('Error! This title is already in use!')
            return
        new_title_result = await set_stream_title(channel_name=msg.channel, title=title)
        if new_title_result:
            await msg.reply('✅')
        else:
            await msg.reply('❌')
        return
    await msg.reply(old_title)


@bot.command(name='game', permissions=['moderador', 'broadcaster'])
async def cmd_game(msg: Message, game: str = None) -> None:
    if game:
        game_data = await get_game(game)
        game_id, game_name = game_data['id'], game_data['name']

        if game_id:
            if await change_stream_game(msg.channel, game_id):
                await msg.reply(f'✅ {game_name}')
            else:
                await msg.reply('❌')
        else:
            await msg.reply('❌ Game not found.')

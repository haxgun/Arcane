from arcane import bot
from arcane.modules.api.twitch import get_stream_title, set_stream_title, change_stream_game, get_game, get_stream_game
from arcane.modules.dataclasses import Message


@bot.command(name='title', permissions=['moderador', 'broadcaster'], cooldown=0)
async def cmd_title(msg: Message, new_title: str = None) -> None:
    old_title = await get_stream_title(channel_name=msg.channel)

    if old_title:
        if new_title and len(new_title) > 3:
            if new_title == old_title:
                await msg.reply('❌ This title is already in use!')
                return
            new_title_result = await set_stream_title(channel_name=msg.channel, title=title)
            if new_title_result:
                await msg.reply('✅')
            else:
                await msg.reply('❌')
            return
        await msg.reply(old_title)
    await msg.reply('Offline')


@bot.command(name='game', permissions=['moderador', 'broadcaster'], cooldown=0)
async def cmd_game(msg: Message, new_game: str = None) -> None:
    old_game = await get_stream_game(msg.channel)
    if old_game:
        if new_game:
            game_data = await get_game(new_game)
            game_id, game_name = game_data['id'], game_data['name']

            if old_game == game_name:
                if game_id:
                    if await change_stream_game(msg.channel, game_id):
                        await msg.reply(f'✅ {game_name}')
                    else:
                        await msg.reply('❌')
                else:
                    await msg.reply('❌ Game not found.')
            else:
                await msg.reply('❌ Game is already set.')
        else:
            await msg.reply(old_game)
    await msg.reply('Offline')

from pony.orm import db_session
from twitchio.ext import commands

from haxbod.bot import Haxbod
from haxbod.models import db
from haxbod.utils.decorators import permission


class Moderator(commands.Cog):
    def __init__(self, bot: Haxbod) -> None:
        self.bot = bot

    @commands.command(name='addcommand', aliases=['addcmd'])
    @permission('moderator', 'broadcaster')
    async def cmd_add_command(self, ctx: commands.Context, *args) -> None:
        if len(args) >= 2:
            command_name = args[0]
            response = ' '.join(args[1:])

            with db_session:
                channel = db.Channel.get(name=ctx.channel.name)

                command = db.Command(
                    name=command_name,
                    response=response,
                    channel=channel.id,
                )

            if command:
                await ctx.reply(f'Command !{command_name} has been added.')
            else:
                await ctx.reply(f'Command !{command_name} already exist.')
        else:
            command = ctx.message.content.split()[0]
            await ctx.reply(f'Usage: {command} <command> <response>')


def prepare(bot: Haxbod) -> None:
    bot.add_cog(Moderator(bot))

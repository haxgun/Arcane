import asyncio
import ssl
import sys
from typing import Optional, Dict, Callable, List

from rich.console import Console

from arcane.models import Channel
from arcane.modules.twitchapi import get_bot_user_id
from arcane.settings import USERNAME, DEBUG, ACCESS_TOKEN, CLIENT_ID
from arcane.modules.dataclasses import Message
from arcane.modules.print import print_success, print_error

console = Console()

TEMPLATE_COMMANDS = {
    '!discord': 'Please join the {message.channel} Discord server, {message.user}',
    '!so': 'Check out {message.content_args[0]}, they are a nice streamer!',
}


class Arcane:
    __slots__ = (
        'ready',
        'host',
        'port',
        'reader',
        'writer',
        'loop',
        'token',
        'username',
        'client_id',
        'id',
        'channels',
        'custom_commands',
    )

    def __init__(self) -> None:
        self.ready: bool = False
        self.host: str = 'irc.chat.twitch.tv'
        self.port: int = 6697
        self.token: str = ACCESS_TOKEN
        self.username: str = USERNAME
        self.client_id: str = CLIENT_ID
        self.channels: List[str] = Channel.get_all_channel_names()
        self.custom_commands: Dict[str, Callable[[Message], None]] = {}

    async def say(self, channel: str, message: str) -> None:
        if len(message) > 500:
            raise Exception(
                "The maximum amount of characters in one message is 500,"
                f" you tried to send {len(message)} characters")

        while message.startswith("."):  # Use Bot.ban, Bot.timeout, etc instead
            message = message[1:]

        await self._send_privmsg(channel, message)

    async def _send_privmsg(self, channel: str, message: str) -> None:
        message = message.replace("\n", " ")
        print(f'> PRIVMSG #{channel} :{message}')
        await self._send_command(f'PRIVMSG #{channel} :{message}')

    async def _nick(self) -> None:
        await self._send_command(f'NICK {self.username}', quiet=True)

    async def _pass(self) -> None:
        await self._send_command(f'PASS oauth:{self.token}', quiet=True)

    async def _send_command(self, command: str, quiet: bool = False) -> None:
        self.writer.write((command + '\r\n').encode())
        return await self.writer.drain()

    async def _capability(self, *args) -> None:
        for arg in args:
            await self._send_command(f'CAP REQ :twitch.tv/{arg}', quiet=True)

    async def join_channel(self, channel) -> None:
        await self._send_command(f'JOIN #{channel}')

    async def part_channel(self, channel) -> None:
        await self._send_command(f'PART #{channel}')

    async def setup(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port, ssl=True)
        self.id = await get_bot_user_id()
        await self._capability('tags', 'commands', 'membership')
        await self._pass()
        await self._nick()
        with console.status("[bold] Connecting to channels...") as status:
            for channel in self.channels:
                await self.join_channel(channel)
        await self.event_ready()
        await self._loop_for_messages()

    async def event_ready(self) -> None:
        if self.ready:
            return

        self.ready = True
        bot_nick = f'[link=https://twitch.tv/{self.username}][yellow]@{self.username}[/link][/yellow]'
        print_success(f'Connected as {bot_nick} with ID: {self.id}')
        channel_connected = ', '.join(
            [f'[link=https://twitch.tv/{channel}][yellow]@{channel}[/link][/yellow]' for channel in
             self.channels])
        print_success(f'Connected to {channel_connected}')
        print_success('Have a nice day!\n')

    def run(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.setup())

    async def _shutdown(self, exit: bool = False) -> None:
        print_error('Goodbey!')
        if self.writer:
            self.writer.close()
            self.loop.create_task(self.writer.wait_closed())

        pending = asyncio.Task.all_tasks()
        gathered = asyncio.gather(*pending)

        try:
            gathered.cancel()
            self.loop.run_until_complete(gathered)
            gathered.exception()
        except:
            pass

        if exit:
            self.loop.stop()
            sys.exit(0)

    async def handle_template_command(self, message: Message, text_command: str, template: str) -> None:
        text = template.format(**{'message': message})
        await self.say(message.channel, text)

    async def handle_message(self, received_msg: str) -> None:
        if len(received_msg) == 0:
            return

        message = Message.parse(received_msg)
        console.print(message)

        # if message.irc_command == 'PING':
        #     """ Tell remote we're still alive """
        #     self._send_command('PONG :tmi.twitch.tv')

        # if DEBUG:
        #     channel_name = f'[purple3][@[link=https://twitch.tv/{message.channel}]{message.channel}][/link][/purple3]'
        #     message_user = f'[link=https://twitch.tv/{message.author}]{message.author}'
        #     console.print(f'[bold]{channel_name} {message_user}[/]: [white]{message.content}')

        # if message.irc_command == 'PRIVMSG':
        #     if message.content_command in TEMPLATE_COMMANDS:
        #         self.handle_template_command(
        #             message,
        #             message.content_command,
        #             TEMPLATE_COMMANDS[message.content_command],
        #         )
        #     if message.content_command in self.custom_commands:
        #         self.custom_commands[message.content_command](message)

    async def _loop_for_messages(self) -> None:
        try:
            while True:
                received_msgs = await self.reader.readline()
                mgs = received_msgs.decode()
                if not mgs:
                    continue
                for msg in mgs.split('\r\n'):
                    await self.handle_message(msg)
        except KeyboardInterrupt:
            await self._shutdown(exit=True)

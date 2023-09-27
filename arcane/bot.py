import asyncio
import importlib
import sys
import traceback
import uuid
from pathlib import Path
from typing import Callable

from rich.console import Console

from arcane.models import Channel
from arcane.modules.api.twitch import get_bot_user_id
from arcane.settings import USERNAME, DEBUG, ACCESS_TOKEN, CLIENT_ID, PREFIX
from arcane.modules.dataclasses import Message, Command
from arcane.modules import print

console = Console()


class Arcane:

    def __init__(self) -> None:
        self.ready: bool = False
        self.host: str = 'irc.chat.twitch.tv'
        self.port: int = 6697
        self.loop: asyncio.AbstractEventLoop | None = None
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.token: str = ACCESS_TOKEN
        self.username: str = USERNAME
        self.client_id: str = CLIENT_ID
        self.id: int | None = None
        self.prefix: str = PREFIX
        self.channels: list[str] = Channel.get_all_channel_names()
        self.commands: dict = {}
        self.aliases: dict = {}
        self.custom_commands: dict[str, Callable[[Message], None]] = {}

    def command(*args, **kwargs):
        return Command(*args, **kwargs)

    async def reply(self, parent: uuid, channel: str, message: str) -> None:
        if len(message) > 500:
            raise Exception(
                'The maximum amount of characters in one message is 500,'
                f' you tried to send {len(message)} characters')

        message = message.replace('\n', ' ')
        await self._send_command(f'@reply-parent-msg-id={parent} PRIVMSG #{channel} :{message}')

    async def say(self, channel: str, message: str) -> None:
        if len(message) > 500:
            raise Exception(
                'The maximum amount of characters in one message is 500,'
                f' you tried to send {len(message)} characters')

        while message.startswith('.'):
            message = message[1:]

        await self._send_privmsg(channel, message)

    async def me(self, channel: str, message: str) -> None:
        if len(message) > 500:
            raise Exception(
                'The maximum amount of characters in one message is 500,'
                f' you tried to send {len(message)} characters')

        message = message.replace('\n', ' ')
        await self._send_command(f'PRIVMSG #{channel} :.me {message}')

    async def _send_privmsg(self, channel: str, message: str) -> None:
        message = message.replace('\n', ' ')
        await self._send_command(f'PRIVMSG #{channel} :{message}')

    async def _nick(self) -> None:
        await self._send_command(f'NICK {self.username}')

    async def _pass(self) -> None:
        await self._send_command(f'PASS oauth:{self.token}')

    async def _send_command(self, command: str) -> None:
        self.writer.write((command + '\r\n').encode())
        return await self.writer.drain()

    async def _capability(self, *args) -> None:
        for arg in args:
            await self._send_command(f'CAP REQ :twitch.tv/{arg}')

    async def join_channel(self, channel) -> None:
        await self._send_command(f'JOIN #{channel}')

    async def part_channel(self, channel) -> None:
        await self._send_command(f'PART #{channel}')

    @staticmethod
    async def load_plugin() -> None:
        extensions = [p.stem for p in Path('./arcane/modules/extensions/').glob('*.py')]
        with console.status('[bold] Installation of extensions begins...'):
            for extension in extensions:
                try:
                    importlib.import_module(f'arcane.modules.extensions.{extension}')
                    print.success(f'\'{extension}\' extension loaded.')
                except Exception as e:
                    print.error(f'\'{extension}\' extension unloaded.')
                    print.error(f'Error: {e}')

    async def setup(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port, ssl=True)
        self.id = await get_bot_user_id()
        await self._capability('tags', 'commands', 'membership')
        await self._pass()
        await self._nick()

        with console.status('[bold] Connecting to channels...'):
            for channel in self.channels:
                await self.join_channel(channel)

        await self.event_ready()
        await self.load_plugin()
        await self._loop_for_messages()

    async def event_ready(self) -> None:
        if self.ready:
            return

        self.ready = True

        if DEBUG:
            console.print('[red bold][!!!!!!] DEBUG MODE ENABLED [!!!!!!][/]')

        bot_nick = f'[link=https://twitch.tv/{self.username}][yellow]@{self.username}[/link][/yellow]'
        print.success(f'Connected as {bot_nick} with ID: {self.id}')
        channel_connected = ', '.join(
            [f'[link=https://twitch.tv/{channel}][yellow]@{channel}[/link][/yellow]' for channel in
             self.channels])
        print.success(f'Connected to {channel_connected}')
        print.success('Have a nice day!\n')

    def run(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.setup())

    async def stop(self, exit: bool = False) -> None:
        print.error('Goodbey!')
        if self.writer:
            self.writer.close()
            self.loop.create_task(self.writer.wait_closed())

        pending = asyncio.Task.all_tasks()
        gathered = asyncio.gather(*pending)

        try:
            gathered.cancel()
            self.loop.run_until_complete(gathered)
            gathered.exception()
        except Exception:
            pass

        if exit:
            self.loop.stop()
            sys.exit(0)

    async def handle_message(self, received_msg: str) -> None:
        if len(received_msg) == 0:
            return

        message = Message.parse(self, received_msg)

        if DEBUG and message:
            console.print(message)

        if message and self.username != message.author:
            channel_name = f'[purple3][@[link=https://twitch.tv/{message.channel}]{message.channel}][/link][/purple3]'
            message_user = (f'[{message.author.color}][link=https://twitch.tv/{message.author}]'
                            f'{message.author.display_name} [/{message.author.color}]')
            console.print(f'[bold][blue][{message.datetime}][/blue] {channel_name} {message_user}[/]: '
                          f'[white]{message.content}')

            if message.content.startswith(self.prefix):
                command = message.content.split()[0][len(self.prefix):]
                if command in self.commands:
                    await self.commands[command].execute_command(message)
                elif command in self.aliases:
                    command = self.aliases[command]
                    await self.commands[command].execute_command(message)

    @staticmethod
    async def parse_error(e: Exception) -> None:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        print.error(f'Ignoring exception in traceback:\n{traceback_str}{e}')

    async def _loop_for_messages(self) -> None:
        while True:
            try:
                received_msgs = await self.reader.readline()
                msgs = received_msgs.decode()
                if not msgs:
                    continue
                for msg in msgs.split('\r\n'):
                    await self.handle_message(msg)
            except Exception as e:
                await self.parse_error(e)


bot = Arcane()

import asyncio
import importlib
import traceback
import uuid
from pathlib import Path
from typing import Callable

from arcane.models import Channel
from arcane.modules import printt, parser, REGEX
from arcane.modules.api.twitch import get_bot_user_id, get_bot_username
from arcane.modules.custom_commands import handle_custom_commands
from arcane.modules.dataclasses import Message, Command, User
from arcane.settings import DEBUG, ACCESS_TOKEN, CLIENT_ID, PREFIX


class Arcane:

    def __init__(self) -> None:
        self.ready: bool = False
        self.host: str = 'irc.chat.twitch.tv'
        self.port: int = 6697
        self.loop: asyncio.AbstractEventLoop | None = None or asyncio.get_event_loop()
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.token: str = ACCESS_TOKEN
        self.username: str | None = None
        self.client_id: str = CLIENT_ID
        self.id: int | None = None
        self.prefix: str = PREFIX
        self.channels: list[str] = Channel.get_all_channel_names()
        self.commands: dict = {}
        self.hidden_commands: dict = {}
        self.aliases: dict = {}
        self.messages: list[Message] = []

    def command(*args, **kwargs) -> Callable[[Message], None]:
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

    async def _pong(self):
        await self._send_command('PONG :tmi.twitch.tv')

    async def _send_privmsg(self, channel: str, message: str) -> None:
        message = message.replace('\n', ' ')
        await self._send_command(f'PRIVMSG #{channel} :{message}')

    async def _nick(self) -> None:
        self.username = await get_bot_username()
        await self._send_command(f'NICK {self.username}')

    async def _pass(self) -> None:
        await self._send_command(f'PASS oauth:{self.token}')

    async def _send_command(self, command: str) -> None:
        self.writer.write((command + '\r\n').encode())
        return await self.writer.drain()

    async def _capability(self, *args) -> None:
        for arg in args:
            await self._send_command(f'CAP REQ :twitch.tv/{arg}')

    async def join_channel(self, channel: str) -> None:
        await self._send_command(f'JOIN #{channel}')

    async def part_channel(self, channel: str) -> None:
        await self._send_command(f'PART #{channel}')

    async def _cache(self, message):
        self.messages.append(message)
        if len(self.messages) > 100:
            self.messages.pop(0)

    @staticmethod
    async def _load_extensions() -> None:
        extension_paths = [p.stem for p in Path('./arcane/modules/extensions/').glob('*.py')]
        with printt.status('[bold] Loading extensions...'):
            for extension in extension_paths:
                try:
                    importlib.import_module(f'arcane.modules.extensions.{extension}')
                    printt.success(f'\'{extension}\' loaded.')
                except Exception as e:
                    printt.error(f'\'{extension}\' failed to load.')
                    printt.error(f'Error: {e}')
        printt.printt()

    async def setup(self) -> None:
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port, ssl=True)
        self.id = await get_bot_user_id()
        await self._capability('tags', 'commands', 'membership')
        await self._pass()
        await self._nick()

        with printt.status('[bold] Connecting to channels...'):
            for channel in self.channels:
                await self.join_channel(channel)

        await self.event_ready()
        await self._load_extensions()
        await self._loop_for_messages()

    async def event_ready(self) -> None:
        if self.ready:
            return

        self.ready = True

        if DEBUG:
            printt.printt('[red bold][!!!!!!] DEBUG MODE ENABLED [!!!!!!][/]')

        bot_nick = f'[link=https://twitch.tv/{self.username}][yellow]@{self.username}[/link][/yellow]'
        printt.success(f'Connected as {bot_nick} with ID: {self.id}')
        channel_connected = ', '.join(
            [f'[link=https://twitch.tv/{channel}][yellow]@{channel}[/link][/yellow]' for channel in
             self.channels])
        printt.success(f'Connected to {channel_connected}')
        printt.success('Have a nice day!\n')

    def run(self) -> None:
        try:
            task_setup = self.setup()
            self.loop.run_until_complete(task_setup)
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            task_stop = self.stop()
            self.loop.run_until_complete(task_stop)
            self.loop.close()

    async def stop(self) -> None:
        if self.writer:
            self.writer.close()

    @staticmethod
    async def parse_error(e: Exception) -> None:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        printt.error(f'Ignoring exception in traceback:\n{traceback_str}{e}')

    async def action_handler(self, message: str) -> None:
        info, action, data, content, channel = await parser(message)

        try:
            if not action:
                return

            elif action == 'PING':
                await self._pong()

            elif action == 'PRIVMSG':
                message_object = Message.parse(self, message)

                if message_object and self.username != message_object.author:
                    channel_name = (f'[purple3][@[link=https://twitch.tv/{message_object.channel}]'
                                    f'{message_object.channel}][/link][/purple3]')
                    message_user = (f'[{message_object.author.color}][link=https://twitch.tv/{message_object.author.name}]'
                                    f'{message_object.author.display_name}[/link][/{message_object.author.color}]')
                    printt.printt(f'[bold][blue][{message_object.datetime}][/blue] {channel_name} {message_user}[/]: '
                                  f'[white]{message_object.content}')

                    if message_object.content.startswith(self.prefix):
                        command = message_object.content.split()[0][len(self.prefix):]
                        if command in self.commands:
                            await self.commands[command].execute_command(message_object)
                        elif command in self.hidden_commands:
                            await self.hidden_commands[command].execute_command(message_object)
                        elif command in self.aliases:
                            command = self.aliases[command]
                            await self.commands[command].execute_command(message_object)
                        else:
                            await handle_custom_commands(message_object)

                await self._cache(message_object)
                await self.event_message(message_object)

            elif action == 'WHISPER':
                message_object = Message.parse(self, message)
                await self._cache(message_object)
                await self.event_private_message(message_object)

            elif action == 'JOIN':
                sender = REGEX['author'].match(data).group('author')
                await self.event_user_join(User(sender, channel))

            elif action == 'PART':
                sender = REGEX['author'].match(data).group('author')
                await self.event_user_leave(User(sender, channel))

            elif action == 'MODE':
                content_data = REGEX['mode'].match(content)
                mode = content_data.group('mode')
                user = content_data.group('user')
                user_object = User(user, channel)

                if mode == '+':
                    await self.event_user_op(user_object)
                else:
                    await self.event_user_deop(user_object)

            elif action == 'USERSTATE':
                if info['mod'] == 1:
                    self.is_mod = True
                else:
                    self.is_mod = False
                await self.event_userstate(User(self.username, channel, info))

            elif action == 'ROOMSTATE':
                await self.event_roomstate(channel, info)

            elif action == 'NOTICE':
                await self.event_notice(channel, info)

            elif action == 'CLEARCHAT':
                if not content:
                    await self.event_clear(channel)
                else:
                    if 'ban-duration' in info.keys():
                        await self.event_timeout(User(content, channel), info)
                    else:
                        await self.event_ban(User(content, channel), info)

            elif action == 'HOSTTARGET':
                m = REGEX['host'].match(content)
                hchannel = m.group('channel')
                viewers = m.group('count')
                if channel == '-':
                    await self.event_host_stop(channel, viewers)
                else:
                    await self.event_host_start(channel, hchannel, viewers)

            elif action == 'USERNOTICE':
                message = content or ''
                user = info['login']
                await self.event_subscribe(Message(message, user, channel, info), info)

            elif action == 'CAP':
                return
            else:
                printt.printt('Unknown event:', action)
                printt.printt(message)

        except Exception as e:
            await self.parse_error(e)

    async def _loop_for_messages(self) -> None:
        while True:
            received_msg = await self.reader.readline()
            message = received_msg.decode().strip()

            if not message:
                continue

            if DEBUG:
                printt.printt(message)

            await self.action_handler(message)

    async def event_message(self, message: Message) -> None:
        pass

    async def event_private_message(self, message: Message) -> None:
        pass

    async def event_user_join(self, user: User) -> None:
        pass

    async def event_user_leave(self, user: User) -> None:
        pass

    async def event_user_op(self, user: User) -> None:
        pass

    async def event_user_deop(self, user: User) -> None:
        pass

    async def event_userstate(self,  user: User) -> None:
        pass

    async def event_roomstate(self, channel, info) -> None:
        pass

    async def event_notice(self, channel, info) -> None:
        pass

    async def event_clear(self, channel) -> None:
        pass

    async def event_timeout(self, user: User, info) -> None:
        pass

    async def event_ban(self, user: User, info) -> None:
        pass

    async def event_host_start(self, channel, hosted_channel, viewer_count) -> None:
        pass

    async def event_host_stop(self, channel, viewer_count) -> None:
        pass

    async def event_subscribe(self, message: Message, tags) -> None:
        pass

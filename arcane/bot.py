import asyncio
import importlib
import traceback
import uuid
from pathlib import Path
from typing import Callable

import aiohttp

from arcane.dataclasses import Message, Command, User
from arcane.models import Channel
from arcane.modules import printt, parser, REGEX
from arcane.modules.api.twitch import get_token_info
from arcane.modules.errors import AuthenticationError
from arcane.settings import DEBUG, ACCESS_TOKEN, CLIENT_ID


class Arcane:
    def __init__(self) -> None:
        self._host: str = 'wss://irc-ws.chat.twitch.tv:443'
        self._loop: asyncio.AbstractEventLoop | None = None or asyncio.get_event_loop()
        self._websocket = None
        self._token: str = ACCESS_TOKEN
        self.username: str | None = None
        self.client_id: str = CLIENT_ID
        self.user_id: int | None = None
        self.prefix: str = '!'
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

    async def send(self, channel: str, message: str) -> None:
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

        while message.startswith('.'):
            message = message[1:]

        await self._send_privmsg(channel, '.me ' + message)

    async def _pong(self):
        await self._send_command('PONG :tmi.twitch.tv')

    async def _send_privmsg(self, channel: str, message: str) -> None:
        message = message.replace('\n', ' ')
        await self._send_command(f'PRIVMSG #{channel} :{message}')

    async def _send_command(self, command: str) -> None:
        await self._websocket.send_str(command + '\r\n')

    async def join_channel(self, channel: str) -> None:
        await self._send_command(f'JOIN #{channel}')

    async def part_channel(self, channel: str) -> None:
        await self._send_command(f'PART #{channel}')

    async def _cache(self, message):
        self.messages.append(message)
        if len(self.messages) > 100:
            self.messages.pop(0)

    async def _load_extensions(self) -> None:
        extension_paths = [p.stem for p in Path('./arcane/extensions/').glob('*.py')]
        with printt.status('[bold] Loading extensions...'):
            for extension in extension_paths:
                try:
                    importlib.import_module(f'arcane.extensions.{extension}')
                    printt.success(f'\'{extension}\' loaded.')
                except Exception as e:
                    printt.error(f'\'{extension}\' failed to load.')
                    await self.parse_error(e)
            printt.printt()

    async def _connect(self) -> None:
        try:
            data = await get_token_info(self._token)
        except AuthenticationError:
            raise AuthenticationError('Invalid or unauthorized Access Token passed.')

        self.username = data['login']
        self.user_id = data['user_id']

        session = aiohttp.ClientSession()
        self._websocket = await session.ws_connect(url=self._host, heartbeat=30.0)

        await self.authenticate()
        await self.event_ready()
        await self._load_extensions()
        await self._loop_for_messages()

    async def authenticate(self) -> None:
        await self._send_command(f'PASS oauth:{self._token}')
        await self._send_command(f'NICK {self.username}')

        for cap in ('tags', 'commands', 'membership'):
            await self._send_command(f'CAP REQ :twitch.tv/{cap}')

        for channel in self.channels:
            await self.join_channel(channel)

    async def event_ready(self) -> None:
        if DEBUG:
            printt.printt('[red bold][!!!!!!] DEBUG MODE ENABLED [!!!!!!][/]')

        bot_nick = f'[link=https://twitch.tv/{self.username}][yellow]@{self.username}[/link][/yellow]'
        printt.success(f'Connected as {bot_nick} with ID: {self.user_id}')
        channel_connected = ', '.join(
            [f'[link=https://twitch.tv/{channel}][yellow]@{channel}[/link][/yellow]' for channel in
             self.channels])
        printt.success(f'Connected to {channel_connected}')
        printt.success('Have a nice day!\n')

    def run(self) -> None:
        try:
            self._loop.run_until_complete(self._connect())
            self._loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self._loop.run_until_complete(self.stop())
            self._loop.close()

    async def stop(self) -> None:
        if self._websocket:
            await self._websocket.close()

    @staticmethod
    async def parse_error(e: Exception) -> None:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        printt.error(f'Ignoring exception in traceback:\n{traceback_str}{e}')

    async def action_handler(self, message: str) -> None:
        tags, action, data, content, channel = await parser(message)

        try:
            if not action:
                return

            elif action == 'PING':
                await self._pong()

            elif action == 'PRIVMSG':
                message_object = Message.parse(self, message)

                if message_object and self.username != message_object.author:
                    channel_name = (f'[purple3][@[link=https://twitch.tv/{message_object.channel.name}]'
                                    f'{message_object.channel.name}][/link][/purple3]')
                    message_user = (f'[{message_object.author.color}][link=https://twitch.tv/{message_object.author.name}]'
                                    f'{message_object.author.display_name}[/link][/{message_object.author.color}]')
                    printt.printt(f'[bold][blue][{message_object.timestamp}][/blue] {channel_name} {message_user}[/]: '
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

                await self._cache(message_object)
                await self.event_message(message_object)

            elif action == 'WHISPER':
                message_object = Message.parse(self, message)
                await self._cache(message_object)
                await self.event_private_message(message_object)

            elif action == 'JOIN':
                sender = REGEX['author'].match(data).group('author')
                user = User(name=sender, channel=channel)
                await self.event_user_join(user)

            elif action == 'PART':
                sender = REGEX['author'].match(data).group('author')
                user = User(name=sender, channel=channel)
                await self.event_user_leave(user)

            elif action == 'MODE':
                content_data = REGEX['mode'].match(content)
                mode = content_data.group('mode')
                user = content_data.group('user')
                user_object = User(name=user, channel=channel)

                if mode == '+':
                    await self.event_user_op(user_object)
                else:
                    await self.event_user_deop(user_object)

            elif action == 'USERSTATE':
                if tags['mod'] == 1:
                    self.is_mod = True
                else:
                    self.is_mod = False
                user = User(name=self.username, channel=channel, tags=tags)
                await self.event_userstate(user)

            elif action == 'ROOMSTATE':
                await self.event_roomstate(channel, tags)

            elif action == 'NOTICE':
                await self.event_notice(channel, tags)

            elif action == 'CLEARCHAT':
                if not content:
                    await self.event_clear(channel)
                else:
                    user = User(name=content, channel=channel)
                    if 'ban-duration' in tags.keys():
                        await self.event_timeout(user, tags)
                    else:
                        await self.event_ban(user, tags)

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
                user = tags['login']
                await self.event_subscribe(Message(message, user, channel, tags), tags)

            elif action == 'CAP':
                return
            else:
                printt.printt('Unknown event:', action)
                printt.printt(message)

        except Exception as e:
            await self.parse_error(e)

    async def _loop_for_messages(self) -> None:
        while True:
            received_msg = await self._websocket.receive()
            if received_msg.type == aiohttp.WSMsgType.TEXT:
                message = received_msg.data.rstrip()

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

    async def event_roomstate(self, channel, tags) -> None:
        pass

    async def event_notice(self, channel, tags) -> None:
        pass

    async def event_clear(self, channel) -> None:
        pass

    async def event_timeout(self, user: User, tags) -> None:
        pass

    async def event_ban(self, user: User, tags) -> None:
        pass

    async def event_host_start(self, channel, hosted_channel, viewer_count) -> None:
        pass

    async def event_host_stop(self, channel, viewer_count) -> None:
        pass

    async def event_subscribe(self, message: Message, tags) -> None:
        pass

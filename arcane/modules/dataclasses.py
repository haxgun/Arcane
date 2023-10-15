import hashlib
import inspect
import struct
import time
from typing import Optional, TYPE_CHECKING

from arcane import settings
from arcane.modules.cooldowns import command_cooldown_manager
from arcane.modules.regex import REGEX

if TYPE_CHECKING:
    from arcane import Arcane


def parse_color(s: str) -> tuple[int, int, int]:
    return int(s[1:3], 16), int(s[3:5], 16), int(s[5:7], 16)


def _gen_color(name: str) -> tuple[int, int, int]:
    h = hashlib.sha256(name.encode())
    n, = struct.unpack('Q', h.digest()[:8])
    bits = [int(s) for s in bin(n)[2:]]

    r = bits[0] * 0b1111111 + (bits[1] << 7)
    g = bits[2] * 0b1111111 + (bits[3] << 7)
    b = bits[4] * 0b1111111 + (bits[5] << 7)
    return r, g, b


class Channel:
    __slots__ = ('_name',)

    def __init__(self, name: str) -> None:
        self._name = name

    def __eq__(self, other):
        return other.name == self._name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return f'<Channel name: {self.name}>'

    @property
    def name(self) -> str:
        """The channel name."""
        return self._name


class User:
    __slots__ = ('name', 'channel', 'id', 'display_name', 'color', 'color_rbg', 'badges', 'is_owner', 'is_broadcaster',
                 'is_moderator', 'is_subscriber', 'is_turbo', 'is_vip', 'tags')

    def __init__(
            self,
            name: str,
            channel: str,
            tags: dict[str, str] = None,
    ) -> None:
        self.name = name
        self.channel = channel

        if tags:
            self.id = tags['user-id'] if 'user-id' in tags else None
            self.display_name = tags['display-name']
            self.color = tags['color']
            self.color_rbg = parse_color(tags['color']) if tags['color'] else _gen_color(self.display_name)
            self.badges = tuple(tags['badges'].split(','))
            self.is_owner = (tags['user-id'] == settings.OWNER_ID) if 'user-id' in tags else None
            self.is_broadcaster = any(badge.startswith('broadcaster/') for badge in self.badges)
            self.is_moderator = any(badge.startswith('moderator/') for badge in self.badges)
            self.is_subscriber = any(badge.startswith(('founder/', 'subscriber/')) for badge in self.badges)
            self.is_turbo = any(badge.startswith('turbo/') for badge in self.badges)
            self.is_vip = any(badge.startswith('vip/') for badge in self.badges)
            self.tags = tags


class Message:
    __slots__ = ('author', 'channel', 'content', 'bot', 'id', 'datetime', 'tags')

    def __init__(
            self,
            author: User,
            channel: "Channel",
            content: str,
            bot: 'Arcane' = None,
            datetime: str = None,
            tags: dict[str, str] = None,
    ) -> None:
        self.author = author
        self.channel = channel
        self.content = content
        self.bot = bot

        if tags:
            self.id = tags['id']
            self.datetime = datetime
            self.tags = tags

    @property
    def bg_color(self) -> tuple[int, int, int] | None:
        if self.tags.get('msg-id') == 'highlighted-message':
            return (117, 94, 188)
        elif 'custom-reward-id' in self.tags:
            return 29, 91, 130
        else:
            return None

    @property
    def optional_user_arg(self) -> str:
        _, _, rest = self.content.strip().partition(' ')
        if rest:
            return rest.lstrip('@')
        else:
            return self.author.display_name

    @classmethod
    def parse(cls, bot, msg) -> Optional['Message']:
        match = REGEX['message'].match(msg)
        if match:

            tags = {}
            for part in match['tags'].split(';'):
                k, v = part.split('=', 1)
                tags[k] = v

            timestamp_ms = int(tags['tmi-sent-ts'])
            time_struct = time.gmtime(timestamp_ms / 1000)
            datetime = time.strftime('%H:%M:%S %d.%m.%Y', time_struct)

            return cls(
                bot=bot,
                datetime=datetime,
                author=User(
                    name=match['author'],
                    channel=match['channel'],
                    tags=tags,
                ),
                channel=Channel(match['channel']),
                content=match['message'],
                tags=tags,
            )
        return None

    async def send(self, message: str) -> None:
        await self.bot.say(self.channel.name, message)

    async def reply(self, message: str) -> None:
        await self.bot.reply(self.id, self.channel.name, message)

    async def me(self, message: str) -> None:
        await self.bot.me(self.channel.name, message)


class Command:
    __slots__ = ('name', 'desc', 'aliases', 'permissions', 'subcommands', 'cooldown', 'bot', 'func')

    def __init__(
            self,
            bot: 'Arcane',
            name: str,
            desc: str = '',
            aliases: list[str] = [],
            permissions: list[str] = [],
            hidden: bool = False,
            cooldown: int = 15,
    ) -> None:
        self.name = name
        self.desc = desc
        self.aliases = aliases
        self.permissions = permissions
        self.subcommands = {}
        self.cooldown = cooldown
        self.bot = bot

        if hidden:
            bot.hidden_commands[name] = self
        else:
            bot.commands[name] = self

        for alias in self.aliases:
            bot.aliases[alias] = name

    def subcommand(self, *args, **kwargs):
        return SubCommand(self, *args, **kwargs)

    def __call__(self, func):
        self.func = func
        return self

    @staticmethod
    def check_user_roles(msg) -> list[str]:
        roles = {
            'owner': msg.author.is_owner,
            'broadcaster': msg.author.is_broadcaster,
            'moderator': msg.author.is_moderator,
            'subscriber': msg.author.is_subscriber,
            'turbo': msg.author.is_turbo,
            'vip': msg.author.is_vip,
        }

        return [role for role, has_role in roles.items() if has_role]

    async def execute_command(self, message: 'Message') -> None:
        if not self.permissions:
            await self.run(message)
        else:
            user_roles = self.check_user_roles(message)
            if any(role in user_roles for role in self.permissions):
                await self.run(message)

    async def run(self, message: 'Message') -> None:
        message_channel = message.channel.name
        args = message.content[len(self.bot.prefix):].split(' ')[1:]

        args_name = inspect.getfullargspec(self.func)[0][1:]

        if len(args) > len(args_name):
            args[len(args_name)-1] = ' '.join(args[len(args_name)-1:])

            args = args[:len(args_name)]

        ann = self.func.__annotations__

        for x in range(len(args_name)):
            try:
                v = args[x]
                k = args_name[x]

                if not isinstance(v, ann[k]):
                    v = ann[k](v)

                args[x] = v
            except IndexError:
                break

        if self.subcommands:
            try:
                subcomm = args.pop(0).split(' ')[0]
            except Exception:
                if command_cooldown_manager.can_use_command(message_channel, self.func, self.cooldown):
                    command_cooldown_manager.update_command_cooldown(message_channel, self.func)
                    await self.func(message, *args)
                return
            if subcomm in self.subcommands:
                c = message.content.split(' ')
                new_content = ' '.join(c[1:])
                await self.subcommands[subcomm].run(Message(
                    bot=message.bot,
                    datetime=message.datetime,
                    author=message.author,
                    channel=message.channel,
                    content=new_content,
                    tags=message.tags,
                ))
            else:
                if command_cooldown_manager.can_use_command(message_channel, self.func, self.cooldown):
                    command_cooldown_manager.update_command_cooldown(message_channel, self.func)
                    await self.func(message, *args)
        else:
            try:
                if command_cooldown_manager.can_use_command(message_channel, self.func, self.cooldown):
                    command_cooldown_manager.update_command_cooldown(message_channel, self.func)
                    await self.func(message, *args)
            except TypeError as e:
                if len(args) < len(args_name):
                    raise Exception(f'Not enough arguments for {self.name}, required arguments: {", ".join(args_name)}')
                else:
                    raise e


class SubCommand(Command):
    __slots__ = ('parent', 'name', 'desc', 'aliases', 'permissions', 'subcommands', 'cooldown', 'bot', 'func')

    def __init__(
            self,
            parent: Command,
            name: str,
            desc: str = '',
            aliases: list[Command] = [],
            permissions: list[str] = [],
            cooldown: int = 15
    ) -> None:
        self.bot = parent.bot
        self.name = name
        self.parent = parent
        self.cooldown = cooldown
        self.subcommands = {}
        parent.subcommands[name] = self
        for alias in aliases:
            parent.subcommands[alias] = self

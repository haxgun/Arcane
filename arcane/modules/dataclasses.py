import datetime
import hashlib
import inspect
import struct
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

    def __init__(self, **kwargs) -> None:
        self._name: str = kwargs.get('name')

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
    __slots__ = ('_tags', '_name', '_channel', '_cached_badges', '_id', '_display_name', '_color', '_badges',
                 '_is_mod', '_is_sub', '_is_turbo', '_is_vip',)

    def __init__(self, **kwargs) -> None:
        self._tags: dict[str, str] | None = kwargs.get('tags')
        self._name: str = kwargs.get('name')
        self._channel: str = kwargs.get('channel') or self._name

        self._cached_badges: dict[str, str] | None = None

        self._id: str | None = None
        self._display_name: str | None = None
        self._color: str | None = None
        self._badges: str | None = None
        self._is_mod: bool | None = None
        self._is_sub: bool | None = None
        self._is_turbo: bool | None = None
        self._is_vip: bool | None = None

        if self._tags:
            self._id: str | None = self._tags.get('user-id')
            self._display_name: str | None = self._tags['display-name']
            self._color: str | None = self._tags['color']
            self._badges: str | None = self._tags.get('badges')
            self._is_mod: bool | None = bool(self._tags['mod'])
            self._is_sub: bool | None = bool(self._tags['subscriber'])
            self._is_turbo: bool | None = bool(self._tags.get('turbo'))
            self._is_vip: bool | None = bool(self._tags.get('vip', 0))

            if self._badges:
                self._cached_badges: dict[str, str] | None = dict([badge.split("/") for badge in self._badges.split(",")])

    def __repr__(self):
        return f"<Chatter name: {self._name}, channel: {self._channel}>"

    @property
    def channel(self):
        return Channel(name=self._channel)

    @property
    def name(self) -> str:
        return self._name or (self.display_name and self.display_name.lower())

    @property
    def badges(self) -> dict:
        return self._cached_badges.copy() if self._cached_badges else {}

    @property
    def display_name(self) -> Optional[str]:
        return self._display_name

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def mention(self) -> str:
        return f"@{self._display_name}"

    @property
    def color(self) -> str:
        return self._color

    @property
    def color_rgb(self) -> tuple[int, int, int]:
        return parse_color(self._tags['color']) if self._tags['color'] else _gen_color(self.display_name)

    @property
    def is_broadcaster(self) -> bool:
        return 'broadcaster' in self.badges

    @property
    def is_mod(self) -> bool | None:
        return True if self._is_mod == 1 else self.channel.name == self.name.lower()

    @property
    def is_moderator(self) -> bool | None:
        return self.is_mod

    @property
    def is_vip(self) -> bool | None:
        return self._is_vip

    @property
    def is_turbo(self) -> bool | None:
        return self._is_turbo

    @property
    def is_subscriber(self) -> bool | None:
        return self._is_sub or 'founder' in self.badges

    @property
    def is_owner(self) -> bool | None:
        return (self._id == settings.OWNER_ID) if self._id else False


class Message:
    __slots__ = ('content', '_author', '_channel', '_bot', '_tags', 'first', '_id', '_timestamp')

    def __init__(self, *args, **kwargs) -> None:
        self.content: str = kwargs.get('content')
        self._author: User = kwargs.get('author')
        self._channel: Channel = kwargs.get('channel')
        self._bot: Arcane = kwargs.get('bot')
        self._tags: dict[str, str] = kwargs.get('tags')

        self.first: bool = False
        if self._tags:
            first = self._tags.get('first-msg')
            if first == '1':
                self.first = True

        try:
            self._id: str = self._tags['id']
            self._timestamp: str = self._tags['tmi-sent-ts']
        except KeyError:
            self._id: None = None
            self._timestamp: datetime = datetime.datetime.now().timestamp() * 1000

    @property
    def id(self) -> str:
        return self._id

    @property
    def author(self) -> 'User':
        return self._author

    @property
    def channel(self) -> 'Channel':
        return self._channel

    @property
    def tags(self) -> dict:
        return self._tags

    @property
    def timestamp(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(int(self._timestamp) / 1000)

    @classmethod
    def parse(cls, bot, msg) -> Optional['Message']:
        match = REGEX['message'].match(msg)
        if match:
            tags = {}
            for part in match['tags'].split(';'):
                k, v = part.split('=', 1)
                tags[k] = v

            return cls(
                content=match['message'],
                author=User(
                    name=match['author'],
                    channel=match['channel'],
                    tags=tags,
                ),
                channel=Channel(
                    name=match['channel'],
                ),
                bot=bot,
                tags=tags,
            )
        return None

    async def send(self, message: str) -> None:
        await self._bot.say(self.channel.name, message)

    async def reply(self, message: str) -> None:
        await self._bot.reply(self.id, self.channel.name, message)

    async def me(self, message: str) -> None:
        await self._bot.me(self.channel.name, message)


class Command:
    __slots__ = ('_bot', '_name', '_aliases', '_permissions', '_hidden', '_cooldown', '_subcommands', 'func')

    def __init__(self, *args, **kwargs) -> None:
        self._bot: Arcane = args[0]
        self._name = kwargs.get('name')
        self._aliases = kwargs.get('aliases', [])
        self._permissions = kwargs.get('permissions', [])
        self._hidden: bool = kwargs.get('hidden', False)
        self._cooldown: float = kwargs.get('cooldown', 15.0)
        self._subcommands = {}

        if self._hidden:
            self._bot.hidden_commands[self._name] = self
        else:
            self._bot.commands[self._name] = self

        for alias in self._aliases:
            self._bot.aliases[alias] = self._name

    def __repr__(self):
        return (f"<Command name: {self._name}, aliases: {self._aliases}, permissions: {self._permissions}, "
                f"hidden: {self._hidden}, cooldown: {self._cooldown}>")

    def __call__(self, func):
        self.func = func
        return self

    def subcommand(self, *args, **kwargs):
        return SubCommand(self, *args, **kwargs)

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
        if not self._permissions:
            await self.run(message)
        else:
            user_roles = self.check_user_roles(message)
            if any(role in user_roles for role in self._permissions):
                await self.run(message)

    async def run(self, message: 'Message') -> None:
        message_channel = message.channel.name
        args = message.content[len(self._bot.prefix):].split(' ')[1:]

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

        if self._subcommands:
            try:
                subcomm = args.pop(0).split(' ')[0]
            except Exception:
                if command_cooldown_manager.can_use_command(message_channel, self.func, self._cooldown):
                    command_cooldown_manager.update_command_cooldown(message_channel, self.func)
                    await self.func(message, *args)
                return
            if subcomm in self._subcommands:
                c = message.content.split(' ')
                content = ' '.join(c[1:])
                await self._subcommands[subcomm].run(Message(
                    content=content,
                    author=message.author,
                    channel=message.channel,
                    bot=self._bot,
                    tags=message.tags,
                ))
            else:
                if command_cooldown_manager.can_use_command(message_channel, self.func, self._cooldown):
                    command_cooldown_manager.update_command_cooldown(message_channel, self.func)
                    await self.func(message, *args)
        else:
            try:
                if command_cooldown_manager.can_use_command(message_channel, self.func, self._cooldown):
                    command_cooldown_manager.update_command_cooldown(message_channel, self.func)
                    await self.func(message, *args)
            except TypeError as e:
                if len(args) < len(args_name):
                    raise Exception(f'Not enough arguments for {self._name}, required arguments:'
                                    f' {", ".join(args_name)}')
                else:
                    raise e


class SubCommand(Command):
    __slots__ = ('_parent', '_name', '_aliases', '_permissions', '_cooldown', '_bot', '_subcommands')

    def __init__(self, *args, **kwargs) -> None:
        self._parent: Command = args[0]
        self._name: str = kwargs.get('name')
        self._aliases: list[Command] = kwargs.get('aliases', [])
        self._permissions: list[str] = kwargs.get('permissions', [])
        self._cooldown: float = kwargs.get('cooldown', 15.0)
        self._bot: Arcane = self._parent._bot
        self._subcommands = {}
        self._parent._subcommands[self._name] = self
        for alias in self._aliases:
            self._parent._subcommands[alias] = self

    def __repr__(self):
        return (f'<SubCommand name: {self._name}, aliases: {self._aliases}, permissions: {self._permissions}, '
                f'cooldown: {self._cooldown}>')


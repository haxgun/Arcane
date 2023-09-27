import hashlib
import inspect
import re
import struct
import time
from typing import Any, Optional, List, NamedTuple

from arcane import settings

MSG_RE = re.compile(
    '^@(?P<info>[^ ]+) :(?P<author>[^!]+).* '
    'PRIVMSG #(?P<channel>[^ ]+) '
    ':(?P<message>[^\r]+)',
)


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


class Author(NamedTuple):
    id: str
    name: str
    display_name: str
    color: str
    badges: tuple[str, ...]
    info: dict[str, str]

    @property
    def color_rbg(self) -> tuple[int, int, int]:
        return parse_color(self.info['color']) if self.info['color'] else _gen_color(self.display_name)

    @property
    def is_owner(self) -> bool:
        return self.info['user-id'] == settings.OWNER_ID

    @property
    def is_broadcaster(self) -> bool:
        return any(badge.startswith('broadcaster/') for badge in self.badges)

    @property
    def is_moderator(self) -> bool:
        return any(badge.startswith('moderator/') for badge in self.badges)

    @property
    def is_subscriber(self) -> bool:
        return any(badge.startswith(('founder/', 'subscriber/')) for badge in self.badges)

    @property
    def is_vip(self) -> bool:
        return any(badge.startswith('vip/') for badge in self.badges)

    @property
    def is_turbo(self) -> bool:
        return any(badge.startswith('turbo/') for badge in self.badges)


class Message(NamedTuple):
    bot: Any
    id: str
    datetime: str
    author: Author
    channel: str
    content: str
    info: dict[str, str]

    @property
    def bg_color(self) -> tuple[int, int, int] | None:
        if self.info.get('msg-id') == 'highlighted-message':
            return (117, 94, 188)
        elif 'custom-reward-id' in self.info:
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
        match = MSG_RE.match(msg)
        if match:

            info = {}
            for part in match['info'].split(';'):
                k, v = part.split('=', 1)
                info[k] = v

            timestamp_ms = int(info['tmi-sent-ts'])
            time_struct = time.gmtime(timestamp_ms / 1000)
            datetime = time.strftime('%H:%M:%S %d.%m.%Y', time_struct)

            return cls(
                bot=bot,
                id=info['id'],
                datetime=datetime,
                author=Author(
                    id=info['user-id'],
                    name=match['author'],
                    display_name=info['display-name'],
                    color=info['color'],
                    badges=tuple(info['badges'].split(',')),
                    info=info,
                ),
                channel=match['channel'],
                content=match['message'],
                info=info,
            )
        return None

    async def send(self, message: str) -> None:
        await self.bot.say(self.channel, message)

    async def reply(self, message: str) -> None:
        await self.bot.reply(self.id, self.channel, message)

    async def me(self, message: str) -> None:
        await self.bot.me(self.channel, message)


class Command:

    def __init__(
            self,
            bot,
            name: str,
            desc: str = '',
            aliases: List[str] = [],
            permissions: List[str] = [],
    ) -> None:
        self.name = name
        self.desc = desc
        self.aliases = aliases
        self.permissions = permissions
        self.subcommands = {}
        self.bot = bot
        bot.commands[name] = self
        for alias in self.aliases:
            bot.commands[alias] = self

    def subcommand(self, *args, **kwargs):
        return SubCommand(self, *args, **kwargs)

    def __call__(self, func):
        self.func = func
        return self

    @staticmethod
    def check_user_roles(msg) -> List[str]:
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
        args = message.content[len(self.bot.prefix):].split(' ')[1:]

        args_name = inspect.getfullargspec(self.func)[0][1:]

        if len(args) > len(args_name):
            args[len(args_name)-1] = ' '.join(args[len(args_name)-1:])

            args = args[:len(args_name)]

        ann = self.func.__annotations__

        for x in range(0, len(args_name)):
            try:
                v = args[x]
                k = args_name[x]

                if not type(v) == ann[k]:
                    try:
                        v = ann[k](v)

                    except Exception:
                        raise TypeError(f'Invalid type: got {ann[k].__name__}, {type(v).__name__} expected')

                args[x] = v
            except IndexError:
                break

        if len(list(self.subcommands.keys())) > 0:
            try:
                subcomm = args.pop(0).split(' ')[0]
            except Exception:
                await self.func(message, *args)
                return
            if subcomm in self.subcommands.keys():
                c = message.content.split(' ')
                new_content = ' '.join(c[1:])
                await self.subcommands[subcomm].run(Message(
                    bot=message.bot,
                    id=message.id,
                    datetime=message.datetime,
                    author=message.author,
                    channel=message.channel,
                    content=new_content,
                    info=message.info,
                ))
            else:
                await self.func(message, *args)

        else:
            try:
                await self.func(message, *args)
            except TypeError as e:
                if len(args) < len(args_name):
                    raise Exception(f'Not enough arguments for {self.name}, required arguments: {", ".join(args_name)}')
                else:
                    raise e


class SubCommand(Command):
    def __init__(self, parent, name, desc='', aliases=[], permissions: List[str] = []) -> None:
        self.bot = parent.bot
        self.name = name
        self.parent = parent
        self.subcommands = {}
        parent.subcommands[name] = self
        for alias in aliases:
            parent.subcommands[alias] = self

import hashlib
import re
import struct
import time
from typing import NamedTuple, Optional

ME_PREFIX = '\x01ACTION '
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


class Message(NamedTuple):
    info: dict[str, str]
    is_me: bool
    author: str
    channel: str
    content: str

    @property
    def id(self) -> str:
        return self.info['id']

    @property
    def badges(self) -> tuple[str, ...]:
        return tuple(self.info['badges'].split(','))

    @property
    def display_name(self) -> str:
        return self.info['display-name']

    @property
    def name_key(self) -> str:
        return self.display_name.lower()

    @property
    def color(self) -> str:
        return self.info['color']

    @property
    def color_rbg(self) -> tuple[int, int, int]:
        if self.info['color']:
            return parse_color(self.info['color'])
        else:
            return _gen_color(self.display_name)

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
            return self.display_name

    @property
    def is_moderator(self) -> bool:
        return any(badge.startswith('moderator/') for badge in self.badges)

    @property
    def is_subscriber(self) -> bool:
        possible = ('founder/', 'subscriber/')
        return any(badge.startswith(possible) for badge in self.badges)

    @property
    def is_vip(self) -> bool:
        return any(badge.startswith('vip/') for badge in self.badges)

    @property
    def datetime(self) -> str:
        timestamp_ms = int(self.info['tmi-sent-ts'])
        time_struct = time.gmtime(timestamp_ms / 1000)
        formatted_time = time.strftime('%H:%M:%S %d.%m.%Y', time_struct)
        return formatted_time

    @classmethod
    def parse(cls, msg: str) -> Optional['Message']:
        match = MSG_RE.match(msg)
        if match:
            is_me = match['message'].startswith(ME_PREFIX)
            if is_me:
                message = match['message'][len(ME_PREFIX):]
            else:
                message = match['message']

            info = {}
            for part in match['info'].split(';'):
                k, v = part.split('=', 1)
                info[k] = v

            return cls(
                info=info,
                is_me=is_me,
                author=match['author'],
                channel=match['channel'],
                content=message
            )
        return None

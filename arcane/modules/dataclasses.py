import re
from typing import NamedTuple, Optional


MSG_RE = re.compile(
    '^@(?P<info>[^ ]+) :(?P<author>[^!]+).* '
    'PRIVMSG #(?P<channel>[^ ]+) '
    ':(?P<message>[^\r]+)',
)


class Message(NamedTuple):
    info: dict[str, str]
    author: str
    channel: str
    message: str

    @classmethod
    def parse(cls, msg: str) -> Optional['Message']:
        match = MSG_RE.match(msg)
        if match:
            info = {}
            for part in match['info'].split(';'):
                k, v = part.split('=', 1)
                info[k] = v

            return cls(
                info=info,
                author=match['author'],
                channel=match['channel'],
                message=match['message']
            )
        return None

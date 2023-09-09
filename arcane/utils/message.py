from typing import NamedTuple


class Message(NamedTuple):
    prefix: str
    author: str
    channel: str
    irc_command: str
    irc_args: list
    content: str
    content_command: str
    content_args: list

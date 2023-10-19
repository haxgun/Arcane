import datetime
from typing import TYPE_CHECKING, Optional

from arcane.dataclasses import User, Channel
from arcane.modules import REGEX

if TYPE_CHECKING:
    from arcane import Arcane


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
        await self._bot.send(self.channel.name, message)

    async def reply(self, message: str) -> None:
        await self._bot.reply(self.id, self.channel.name, message)

    async def me(self, message: str) -> None:
        await self._bot.me(self.channel.name, message)

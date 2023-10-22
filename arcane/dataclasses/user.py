import hashlib
import struct

from arcane import settings
from arcane.dataclasses import Channel


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
            self._display_name: str | None = self._tags.get('display-name')
            self._color: str | None = self._tags.get('color')
            self._badges: str | None = self._tags.get('badges')
            self._is_mod: bool | None = bool(self._tags['mod'])
            self._is_sub: bool | None = bool(self._tags['subscriber'])
            self._is_turbo: bool | None = bool(self._tags.get('turbo'))
            self._is_vip: bool | None = bool(self._tags.get('vip', 0))

            if self._badges:
                self._cached_badges: dict[str, str] | None = dict([badge.split('/') for badge in self._badges.split(',')])

    def __repr__(self):
        return f'<Chatter name: {self._name}, channel: {self._channel}>'

    @property
    def channel(self) -> Channel:
        return Channel(name=self._channel)

    @property
    def name(self) -> str:
        return self._name or (self.display_name and self.display_name.lower())

    @property
    def badges(self) -> dict:
        return self._cached_badges.copy() if self._cached_badges else {}

    @property
    def display_name(self) -> str | None:
        return self._display_name

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def mention(self) -> str:
        return f'@{self._display_name}'

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

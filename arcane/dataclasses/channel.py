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
    
import inspect
from typing import TYPE_CHECKING

from arcane.dataclasses import Message
from arcane.modules.cooldowns import command_cooldown_manager

if TYPE_CHECKING:
    from arcane import Arcane


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
        return (f'<Command name: {self._name}, aliases: {self._aliases}, permissions: {self._permissions}, '
                f'hidden: {self._hidden}, cooldown: {self._cooldown}>')

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

    async def execute_command(self, message: Message) -> None:
        if not self._permissions:
            await self.run(message)
        else:
            user_roles = self.check_user_roles(message)
            if any(role in user_roles for role in self._permissions):
                await self.run(message)

    async def run(self, message: Message) -> None:
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

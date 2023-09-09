import socket
import ssl
from typing import Optional, Dict, Callable, List

from rich.console import Console

from arcane.models import Channel
from arcane.settings import OAUTH_TOKEN, USERNAME, irc_server, irc_port, DEBUG
from arcane.utils.message import Message
from arcane.utils.print import print_success, print_error

console = Console()



class Arcane:
    __slots__ = ('ready', 'irc', 'irc_server', 'irc_port', 'oauth_token', 'username', 'channels', 'custom_commands')

    def __init__(self) -> None:
        self.ready = False
        self.irc = ssl.wrap_socket(socket.socket())
        self.irc_server: str = irc_server
        self.irc_port: int = irc_port
        self.oauth_token: str = OAUTH_TOKEN
        self.username: str = USERNAME
        self.channels: List[str] = Channel.get_all_channel_names()
        self.custom_commands: Dict[str, Callable[[Message], None]] = {
            # '!date': self.reply_with_date,
            # '!ping': self.reply_to_ping,
            # '!randint': self.reply_with_randint,
        }

    def send_privmsg(self, channel: str, text: str) -> None:
        self.send_command(f'PRIVMSG #{channel} :{text}')

    def send_command(self, command: str, quiet: bool = False) -> None:
        self.irc.send((command + '\r\n').encode())

    def setup(self) -> None:
        self.irc.connect((self.irc_server, self.irc_port))
        self.send_command('CAP REQ :twitch.tv/tags', quiet=True)
        self.send_command(f'PASS {self.oauth_token}', quiet=True)
        self.send_command(f'NICK {self.username}', quiet=True)
        with console.status("[bold]We go to the channels...") as status:
            for channel in self.channels:
                self.send_command(f'JOIN #{channel}')
        self.event_ready()
        self.loop_for_messages()

    def event_ready(self) -> None:
        if self.ready:
            return

        self.ready = True
        bot_nick = f'[link=https://twitch.tv/{self.username}][yellow]@{self.username}[/link][/yellow]'
        print_success(f'Connected as {bot_nick}')
        channel_connected = ', '.join(
            [f'[link=https://twitch.tv/{channel}][yellow]@{channel}[/link][/yellow]' for channel in
             self.channels])
        print_success(f'Connected to {channel_connected}')
        print_success('Have a nice day!\n')

    def run(self) -> None:
        self.setup()

    @staticmethod
    def get_user_from_prefix(prefix: str) -> Optional[str]:
        domain = prefix.split('!')[0]
        if domain.endswith('.tmi.twitch.tv'):
            return domain.replace('.tmi.twitch.tv', '')
        if 'tmi.twitch.tv' not in domain:
            return domain
        return None

    def parse_message(self, received_msg: str) -> Message:
        parts = received_msg.split(' ')

        prefix = None
        author = None
        channel = None
        content = None
        content_command = None
        content_args = None
        irc_command = None
        irc_args = None

        if parts[0].startswith(':'):
            prefix = parts[0][1:]
            author = self.get_user_from_prefix(prefix)
            parts = parts[1:]

        text_start = next(
            (idx for idx, part in enumerate(parts) if part.startswith(':')),
            None
        )
        if text_start is not None:
            text_parts = parts[text_start:]
            text_parts[0] = text_parts[0][1:]
            content = ' '.join(text_parts)
            content_command = text_parts[0]
            content_args = text_parts[1:]
            parts = parts[:text_start]

        irc_command = parts[0]
        irc_args = parts[1:]

        hash_start = next(
            (idx for idx, part in enumerate(irc_args) if part.startswith('#')),
            None
        )
        if hash_start is not None:
            channel = irc_args[hash_start][1:]

        message = Message(
            prefix=prefix,
            author=author,
            channel=channel,
            irc_command=irc_command,
            irc_args=irc_args,
            content=content,
            content_command=content_command,
            content_args=content_args
        )

        return message

    def handle_template_command(self, message: Message, text_command: str, template: str) -> None:
        text = template.format(**{'message': message})
        self.send_privmsg(message.channel, text)

    def handle_message(self, received_msg: str) -> None:
        if len(received_msg) == 0:
            return
        msg = received_msg.split()

        if ':tmi.twitch.tv' not in msg:
            console.print(received_msg)

        # message = self.parse_message(received_msg)
        # if DEBUG:
        #     channel_name = f'[purple3][@[link=https://twitch.tv/{message.channel}]{message.channel}][/link][/purple3]'
        #     message_user = f'[link=https://twitch.tv/{message.author}]{message.author}'
        #     console.print(f'[bold]{channel_name} {message_user}[/]: [white]{message.content}')
        #
        # if message.irc_command == 'PRIVMSG':
        #     if message.content_command in TEMPLATE_COMMANDS:
        #         self.handle_template_command(
        #             message,
        #             message.content_command,
        #             TEMPLATE_COMMANDS[message.content_command],
        #         )
        #     if message.content_command in self.custom_commands:
        #         self.custom_commands[message.content_command](message)

    def loop_for_messages(self) -> None:
        try:
            while True:
                received_msgs = self.irc.recv(2048).decode()
                for received_msg in received_msgs.split('\r\n'):
                    self.handle_message(received_msg)
        except KeyboardInterrupt:
            print_error('Goodbye!')
        except Exception:
            pass

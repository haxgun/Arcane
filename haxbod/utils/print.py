from rich.console import Console
from rich.prompt import Prompt

console = Console()


def print_success(message):
    console.print(f'[bold green][+] [white]{message}[/]')


def print_error(message):
    console.print(f'[bold red][!] [white]{message}[/]')


def print_loading(message):
    console.print(f'[bold yellow][\] [white]{message}[/]')


def print_info(message):
    console.print(f'[bold green][?] [white]{message}[/]')


def input_answer(message):
    return Prompt.ask(f'[bold green][?] [white]{message}[/]')

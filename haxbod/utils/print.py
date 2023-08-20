from rich.console import Console
from rich.prompt import Prompt

console = Console()


def print_success(message) -> None:
    console.print(f'[bold green][+] [white]{message}[/]')


def print_error(message) -> None:
    console.print(f'[bold red][!] [white]{message}[/]')


def print_loading(message) -> None:
    console.print(f'[bold yellow][\] [white]{message}[/]')


def print_info(message) -> None:
    console.print(f'[bold green][?] [white]{message}[/]')


def input_answer(message) -> None:
    return Prompt.ask(f'[bold green][?] [white]{message}[/]')

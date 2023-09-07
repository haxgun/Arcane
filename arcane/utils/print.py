from rich.console import Console
from rich.prompt import Prompt

console = Console()


def print_success(message: str) -> None:
    console.print(f'[bold green][+] [white]{message}[/]')


def print_error(message: str) -> None:
    console.print(f'[bold red][!] [white]{message}[/]')


def print_loading(message: str) -> None:
    console.print(f'[bold yellow][\] [white]{message}[/]')


def print_info(message: str) -> None:
    console.print(f'[bold green][?] [white]{message}[/]')


def input_answer(message: str) -> None:
    return Prompt.ask(f'[bold green][?] [white]{message}[/]')

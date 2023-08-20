from colorama import Fore, Style

SB = Style.BRIGHT
RS = Style.RESET_ALL
W = Fore.WHITE
G = Fore.GREEN
R = Fore.RED
Y = Fore.YELLOW


def print_success(message):
    print(f'{SB}{Y}[+] {W}{message}{RS}')


def print_error(message):
    print(f'{SB}{R}[!] {W}{message}{RS}')


def print_info(message):
    print(f'{SB}{G}[?] {W}{message}{RS}')


def input_answer(message):
    return input(f'{SB}{G}[?] {W}{message} {RS}')

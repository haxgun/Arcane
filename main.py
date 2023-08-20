# !/usr/bin/env python

import argparse

from pony.orm import db_session

from haxbod.bot import Haxbod
from haxbod.models import db

from colorama import Fore, Style

from haxbod.utils.twitchapi import channel_exists

bot = Haxbod()

SB = Style.BRIGHT
RS = Style.RESET_ALL
W = Fore.WHITE
G = Fore.GREEN
R = Fore.RED
Y = Fore.YELLOW


def add_channel():
    channel_name = str(input(f'{SB}{G}[?] {W}Which channel do you want to add? {RS}'))

    if len(channel_name.split()) == 1:
        try:
            channel_exists(channel_name)
        except Exception as e:
            print('There is no such user!')
            return

        with db_session:
            existing_channel = db.Channel.get(name=channel_name)

            if existing_channel:
                print(f'{SB}{R}[!] {W}User {G}@{channel_name}{W} already exists.')
            else:
                channel = db.Channel(name=channel_name)
                print(f'{SB}{Y}[+] {W}User {G}@{channel_name}{W} added.')
    else:
        raise ValueError(f'{SB}{Y}[!] {W}Enter the correct channel value.')


def run_bot():
    bot.run()


def remove_channel():
    channel_name = str(input(f'{SB}{G}[?] {W}Which channel do you want to remove? {RS}'))

    if len(channel_name.split()) == 1:
        with db_session:
            existing_channel = db.Channel.get(name=channel_name)

            if existing_channel:
                existing_channel.delete()
                print(f'{SB}{Y}[-] {W}User {G}@{channel_name}{W} has been removed from the database.')
            else:
                print(f'{SB}{R}[!] {W}User {G}@{channel_name}{W} is not in the database.')
    else:
        raise ValueError(f'{SB}{R}[!] {W}Enter the correct channel value.')


def main():
    command_functions = {
        'addchannel': add_channel,
        'runbot': run_bot,
        'removechannel': remove_channel
    }

    parser = argparse.ArgumentParser(description='Script to interact with your Twitch bot')
    parser.add_argument('command', choices=command_functions.keys(), help='Specify the command to execute')

    args = parser.parse_args()

    selected_function = command_functions[args.command]
    selected_function()


if __name__ == '__main__':
    main()

# !/usr/bin/env python

import argparse

from pony.orm import db_session

from haxbod.bot import Haxbod
from haxbod.models import db
from haxbod.utils.twitchapi import existing_channel_twitch
from haxbod.utils.print import print_success, print_error, input_answer

bot = Haxbod()


def add_channel():
    channel_name = str(input_answer('Which channel do you want to add?'))

    if not existing_channel_twitch(channel_name):
        print_error('There is no such user!')
        return

    with db_session:
        existing_channel_db = db.Channel.get(name=channel_name)

        if not existing_channel_db:
            channel = db.Channel(name=channel_name)
            print_success(f'User @{channel_name} added.')
        else:
            print_error(f'User @{channel_name} already exists.')


def run_bot():
    bot.run()


def remove_channel():
    channel_name = str(input_answer('Which channel do you want to add?'))

    with db_session:
        existing_channel = db.Channel.get(name=channel_name)

        if existing_channel:
            existing_channel.delete()
            print_success(f'User @{channel_name} has been removed from the database.')
        else:
            print_error(f'User @{channel_name} is not in the database.')


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

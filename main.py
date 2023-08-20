# !/usr/bin/env python
"""Haxbod command-line utility for administrative tasks."""

import argparse

from haxbod.utils.print import print_error
from haxbod.utils.command_line_arguments import add_channel, run_bot, remove_channel


def main():
    """Run administrative tasks."""
    command_functions = {
        'addchannel': add_channel,
        'runbot': run_bot,
        'removechannel': remove_channel
    }

    command_descriptions = {
        'addchannel': 'Add a channel to the bot',
        'runbot': 'Run the bot',
        'removechannel': 'Remove a channel from the bot'
    }

    parser = argparse.ArgumentParser(description='Script to interact with your Twitch bot')

    subparsers = parser.add_subparsers(dest='command', help='Specify the command to execute')

    addchannel_parser = subparsers.add_parser('addchannel', help=command_descriptions['addchannel'])
    runbot_parser = subparsers.add_parser('runbot', help=command_descriptions['runbot'])
    removechannel_parser = subparsers.add_parser('removechannel', help=command_descriptions['removechannel'])

    args = parser.parse_args()

    try:
        selected_function = command_functions[args.command]
        selected_function()
    except KeyError:
        print_error('No argument selected')


if __name__ == '__main__':
    main()

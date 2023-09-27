# !/usr/bin/env python
"""Arcane command-line utility for administrative tasks."""

import argparse

from arcane.modules import print
from arcane.modules.cla import add_channel, run_bot, remove_channel


def main():
    """Run administrative tasks."""
    command_functions = {
        'addchannel': add_channel,
        'run': run_bot,
        'removechannel': remove_channel
    }

    command_descriptions = {
        'addchannel': 'Add a channel to the bot',
        'run': 'Run the bot',
        'removechannel': 'Remove a channel from the bot'
    }

    parser = argparse.ArgumentParser(description='Script to interact with your Twitch bot')

    subparsers = parser.add_subparsers(dest='command', help='Specify the command to execute')

    addchannel_parser = subparsers.add_parser('addchannel', help=command_descriptions['addchannel'])
    runbot_parser = subparsers.add_parser('run', help=command_descriptions['run'])
    removechannel_parser = subparsers.add_parser('removechannel', help=command_descriptions['removechannel'])

    args = parser.parse_args()

    try:
        selected_function = command_functions[args.command]
        selected_function()
    except KeyError:
        print.error('No argument selected')


if __name__ == '__main__':
    main()

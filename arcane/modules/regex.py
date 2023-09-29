import re

REGEX = {
    'data': re.compile(
        r'^(?:@(?P<info>\S+)\s)?:(?P<data>\S+)(?:\s)'
        r'(?P<action>[A-Z]+)(?:\s#)(?P<channel>\S+)'
        r'(?:\s(?::)?(?P<content>.+))?'),
    'message': re.compile(
        r'^@(?P<info>[^ ]+) :(?P<author>[^!]+).* '
        r'PRIVMSG #(?P<channel>[^ ]+) '
        r':(?P<message>[^\r]+)'),
    'ping': re.compile('PING (?P<content>.+)'),
    'author': re.compile(
        '(?P<author>[a-zA-Z0-9_]+)!(?P=author)'
        '@(?P=author).tmi.twitch.tv'),
    'mode': re.compile('(?P<mode>[\+\-])o (?P<user>.+)'),
    'host': re.compile(
        '(?P<channel>[a-zA-Z0-9_]+) '
        '(?P<count>[0-9\-]+)')}
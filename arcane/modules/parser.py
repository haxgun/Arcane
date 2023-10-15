from typing import Match

from arcane.modules.regex import REGEX


async def get_tags(message: Match) -> dict | None:
    try:
        tags = message.group('tags')
        tags_dict = {}
        for data in tags.split(';'):
            variable = data.split('=')
            if variable[1].isnumeric():
                variable[1] = int(variable[1])
            tags_dict[variable[0]] = variable[1]
        return tags_dict
    except Exception:
        return None


async def parser(message: str) -> tuple:
    try:
        regex_template = REGEX['ping'] if message.startswith('PING') else REGEX['data']
        message_data = regex_template.match(message)
        tags = await get_tags(message_data)

        try:
            action = message_data.group('action')
        except Exception:
            action = 'PING'

        try:
            data = message_data.group('data')
        except Exception:
            data = None

        try:
            content = message_data.group('content')
        except Exception:
            content = None

        try:
            channel = message_data.group('channel')
        except Exception:
            channel = None

        return tags, action, data, content, channel
    except Exception:
        pass

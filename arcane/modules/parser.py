from typing import Match

from arcane.modules.regex import REGEX


async def get_info(message: Match) -> dict | None:
    try:
        info = message.group('info')
        info_dict = {}
        for data in info.split(';'):
            variable = data.split('=')
            if variable[1].isnumeric():
                variable[1] = int(variable[1])
            info_dict[variable[0]] = variable[1]
        return info_dict
    except Exception:
        return None


async def parser(message: str) -> tuple:
    try:
        regex_template = REGEX['ping'] if message.startswith('PING') else REGEX['data']
        message_data = regex_template.match(message)
        info = await get_info(message_data)

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

        return info, action, data, content, channel
    except Exception:
        pass

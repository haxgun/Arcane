import time
from datetime import datetime

import aiohttp
import pytz
import requests
from dateutil.parser import parse as parse_datetime

from arcane import settings
from arcane.modules.errors import AuthenticationError, HTTPException

session = aiohttp.ClientSession()

bot_headers = {
    'Client-ID': settings.CLIENT_ID,
    'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
}


async def get_token_info(token):
    url = 'https://id.twitch.tv/oauth2/validate'
    headers = {'Authorization': f'OAuth {token}'}

    async with session.get(url=url, headers=headers) as resp:
        if resp.status == 401:
            raise AuthenticationError('Invalid or unauthorized Access Token passed.')
        if resp.status > 300 or resp.status < 200:
            raise HTTPException('Unable to validate Access Token: ' + await resp.text())
        data: dict = await resp.json()
        return data


def existing_channel_twitch(channel_name: str) -> bool:
    url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    response = requests.get(url, headers=bot_headers)
    if response.ok and response.json().get('data'):
        return True
    return False


async def get_stream(channel_name: str) -> list | None:
    url = f'https://api.twitch.tv/helix/streams?user_login={channel_name}'
    async with session.get(url, headers=bot_headers) as response:
        if response.status == 200:
            data = await response.json()
            return data['data']
        return


async def get_user(channel_name: str) -> dict | None:
    url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    async with session.get(url, headers=bot_headers) as response:
        if response.status == 200:
            data = await response.json()
            return data['data']
        return


async def get_stream_started_at(channel_name: str) -> datetime | None:
    data = await get_stream(channel_name)
    if data and len(data) > 0:
        started_at_str = data[0]['started_at']
        return parse_datetime(started_at_str).replace(tzinfo=pytz.UTC)
    return


async def api_latency() -> int | None:
    start_time = time.time()

    async with session.get('https://gql.twitch.tv/gql', timeout=5):
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        return latency

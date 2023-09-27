import time
from datetime import datetime
from typing import Optional

import aiohttp
import pytz
import requests
from dateutil.parser import parse as parse_datetime

from arcane import settings
from arcane.modules import print

headers = {
    'Client-ID': settings.CLIENT_ID,
    'Authorization': f'Bearer {settings.ACCESS_TOKEN}'
}

headers_broadcaster = {
    'Client-ID': settings.BROADCASTER_CLIENT_ID,
    'Authorization': f'Bearer {settings.BROADCASTER_TOKEN}'
}


async def get_bot_username() -> str:
    url = 'https://api.twitch.tv/helix/users'
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            try:
                data = await response.json()
                if 'data' in data and len(data['data']) > 0:
                    return data['data'][0]['login']
            except Exception as e:
                print.error(f'Error: {e}')


async def get_bot_user_id() -> int:
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.twitch.tv/helix/users', headers=headers) as response:
            data = await response.json()
            if 'data' in data and len(data['data']) > 0:
                return data['data'][0]['id']


def existing_channel_twitch(channel_name: str) -> bool:
    url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    response = requests.get(url, headers=headers)
    if response.ok and response.json().get('data'):
        return True
    return False


async def get_stream(channel_name: str) -> list | None:
    url = f'https://api.twitch.tv/helix/streams?user_login={channel_name}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['data']
            return


async def get_user(channel_name: str) -> dict | None:
    url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            return


async def get_broadcaster_id(channel_name: str) -> str | None:
    data = await get_user(channel_name)
    if data:
        return data['data'][0]['id']
    return


async def get_user_creation(channel_name: str) -> datetime | None:
    data = await get_user(channel_name)
    if data:
        created_at_str = data['data'][0]['created_at']
        return parse_datetime(created_at_str).replace(tzinfo=pytz.UTC)
    return


async def get_stream_title(channel_name: str) -> str | None:
    data = await get_stream(channel_name)
    if data:
        return data[0]['title']
    return


async def get_stream_started_at(channel_name: str) -> datetime | None:
    data = await get_stream(channel_name)
    if data:
        started_at_str = data[0]['started_at']
        return parse_datetime(started_at_str).replace(tzinfo=pytz.UTC)
    return


async def get_followers(channel_name: str) -> list | None:
    channel_id = await get_broadcaster_id(channel_name)
    url = f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={channel_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['data']
            return


async def get_followers_count(channel_name: str) -> list | None:
    channel_id = await get_broadcaster_id(channel_name)
    url = f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={channel_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['total']
            return


async def get_game_id(new_game: str) -> Optional[str]:
    url = f'https://api.twitch.tv/helix/search/categories?query={new_game}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['data'][0]['id']
            return


async def get_game_name(new_game: str) -> Optional[str]:
async def get_game(new_game: str) -> tuple[str, str] | None:
    url = f'https://api.twitch.tv/helix/search/categories?query={new_game}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['data'][0]['name']
            return


async def change_stream_game(channel_name: str, game_id: str) -> bool:
    channel_id = await get_broadcaster_id(channel_name)
    if channel_id:
        url = f'https://api.twitch.tv/helix/channels?broadcaster_id={channel_id}'
        payload = {'game_id': game_id}
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers_broadcaster, json=payload) as response:
                if response.status == 204:
                    return True
    return False


async def set_stream_title(channel_name: str, *, title: str) -> bool:
    channel_id = await get_broadcaster_id(channel_name)
    if channel_id:
        url = f'https://api.twitch.tv/helix/channels?broadcaster_id={channel_id}'
        payload = {'title': title}
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers_broadcaster, json=payload) as response:
                if response.status == 204:
                    return True
    return False


async def api_latency() -> int | None:
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        async with session.get('https://gql.twitch.tv/gql', timeout=5):
            end_time = time.time()
            latency = round((end_time - start_time) * 1000)
            return latency

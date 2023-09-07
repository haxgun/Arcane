import time
from datetime import datetime

import pytz
from dateutil.parser import parse as parse_datetime
from typing import Optional

import aiohttp
import requests
from arcane import settings

client_id = settings.CLIENT_ID
access_token = settings.ACCESS_TOKEN
headers = {
    'Client-ID': client_id,
    'Authorization': f'Bearer {access_token}'
}


def existing_channel_twitch(channel_name: str) -> bool:
    url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    response = requests.get(url, headers=headers)
    if response.ok and response.json().get('data'):
        return True
    return False


async def get_stream(channel_name: str) -> Optional[list]:
    url = f'https://api.twitch.tv/helix/streams?user_login={channel_name}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['data']
            return


async def get_user(channel_name: str) -> Optional[dict]:
    url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            return


async def get_broadcaster_id(channel_name: str) -> Optional[str]:
    data = await get_user(channel_name)
    if data:
        return data['data'][0]['id']
    return


async def get_user_creation(channel_name: str) -> Optional[datetime]:
    data = await get_user(channel_name)
    if data:
        created_at_str = data['data'][0]['created_at']
        return parse_datetime(created_at_str).replace(tzinfo=pytz.UTC)
    return


async def get_stream_title(channel_name: str) -> Optional[str]:
    data = await get_stream(channel_name)
    if data:
        return data[0]['title']
    return


async def get_stream_started_at(channel_name: str) -> Optional[datetime]:
    data = await get_stream(channel_name)
    if data:
        started_at_str = data[0]['started_at']
        return parse_datetime(started_at_str).replace(tzinfo=pytz.UTC)
    return


async def get_followers(channel_name: str) -> Optional[list]:
    channel_id = await get_broadcaster_id(channel_name)
    url = f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={channel_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data['data']
            return


async def get_followers_count(channel_name: str) -> Optional[list]:
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
                return data["data"][0]["id"]
            return


async def get_game_name(new_game: str) -> Optional[str]:
    url = f'https://api.twitch.tv/helix/search/categories?query={new_game}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"][0]["name"]
            return


async def change_stream_game(channel_name: str, game_id: str) -> bool:
    channel_id = await get_broadcaster_id(channel_name)
    if channel_id:
        url = f'https://api.twitch.tv/helix/channels?broadcaster_id={channel_id}'
        payload = {'game_id': game_id}
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=payload) as response:
                if response.status == 204:
                    return True
    return False


async def set_stream_title(channel_name: str, *, title: str) -> bool:
    channel_id = await get_broadcaster_id(channel_name)
    if channel_id:
        url = f'https://api.twitch.tv/helix/channels?broadcaster_id={channel_id}'
        payload = {'title': title}
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=payload) as response:
                if response.status == 204:
                    return True
    return False


async def api_latency() -> Optional[int]:
    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        async with session.get('https://gql.twitch.tv/gql', timeout=5) as response:
            end_time = time.time()
            latency = round((end_time - start_time) * 1000)
            return latency

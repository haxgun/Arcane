import time
from datetime import datetime

import aiohttp
import pytz
import requests
from dateutil.parser import parse as parse_datetime
from fuzzywuzzy import fuzz

from arcane import settings
from arcane.models import Channel
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


async def get_user_id(channel_name: str) -> str | None:
    data = await get_user(channel_name)
    if data:
        return data[0]['id']
    return


async def get_user_creation(channel_name: str) -> datetime | None:
    data = await get_user(channel_name)
    if data:
        created_at_str = data[0]['created_at']
        return parse_datetime(created_at_str).replace(tzinfo=pytz.UTC)
    return


async def get_stream_game(channel_name: str) -> str | None:
    data = await get_stream(channel_name)
    if data and len(data) > 0:
        return data[0]['game_name']
    return


async def get_stream_title(channel_name: str) -> str | None:
    data = await get_stream(channel_name)
    if data and len(data) > 0:
        return data[0]['title']
    return


async def get_stream_started_at(channel_name: str) -> datetime | None:
    data = await get_stream(channel_name)
    if data and len(data) > 0:
        started_at_str = data[0]['started_at']
        return parse_datetime(started_at_str).replace(tzinfo=pytz.UTC)
    return


async def get_followers(channel_name: str) -> list | None:
    channel_id = await get_user_id(channel_name)
    url = f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={channel_id}'
    async with session.get(url, headers=bot_headers) as response:
        if response.status == 200:
            data = await response.json()
            return data['data']
        return


async def get_followers_count(channel_name: str) -> list | None:
    channel_id = await get_user_id(channel_name)
    url = f'https://api.twitch.tv/helix/channels/followers?broadcaster_id={channel_id}'
    async with session.get(url, headers=bot_headers) as response:
        if response.status == 200:
            data = await response.json()
            return data['total']
        return


def find_most_similar_game(games_data, game_to_find):
    max_similarity = -1
    most_similar_game = None

    for game_data in games_data:
        game_name = game_data['name']
        similarity = fuzz.ratio(game_to_find.lower(), game_name.lower())

        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_game = game_data

    return most_similar_game


async def get_game(new_game: str) -> tuple[str, str] | None:
    url = f'https://api.twitch.tv/helix/search/categories?query={new_game}'
    async with session.get(url, headers=bot_headers) as response:
        if response.status == 200:
            data = await response.json()
            return find_most_similar_game(data['data'], new_game)
        return


async def change_stream_game(channel_name: str, game_id: str) -> bool:
    channel_id = await get_user_id(channel_name)
    if channel_id:
        url = f'https://api.twitch.tv/helix/channels?broadcaster_id={channel_id}'

        channel = Channel.get(Channel.name == channel_name)
        client_id = channel.cliend_id
        oauth = channel.oauth

        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {oauth}'
        }

        payload = {'game_id': game_id}
        async with session.patch(url, headers=headers, json=payload) as response:
            if response.status == 204:
                return True
    return False


async def set_stream_title(channel_name: str, *, title: str) -> bool:
    channel_id = await get_user_id(channel_name)
    if channel_id:
        url = f'https://api.twitch.tv/helix/channels?broadcaster_id={channel_id}'

        channel = Channel.get(Channel.name == channel_name)
        client_id = channel.cliend_id
        oauth = channel.oauth

        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {oauth}'
        }

        payload = {'title': title}

        async with session.patch(url, headers=headers, json=payload) as response:
            if response.status == 204:
                return True
    return False


async def api_latency() -> int | None:
    start_time = time.time()

    async with session.get('https://gql.twitch.tv/gql', timeout=5):
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        return latency

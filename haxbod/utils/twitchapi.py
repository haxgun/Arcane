import aiohttp
import requests
from haxbod import settings

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


async def get_broadcaster_id(channel_name: str) -> str | None:
    url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                user_id = data['data'][0]['id']
                return user_id
            return


async def get_stream_title(channel_name: str) -> str | None:
    channel_id = await get_broadcaster_id(channel_name)
    url = f'https://api.twitch.tv/helix/channels?broadcaster_id={channel_id}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                title = data['data'][0]['title']
                return title
            return


async def cmd_set_stream_title(channel_name, *, title: str) -> bool:
    channel_id = await get_broadcaster_id(channel_name)
    if channel_id is not None:
        url = f'https://api.twitch.tv/helix/channels?broadcaster_id={channel_id}'
        payload = {
            'title': title
        }
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=payload) as response:
                if response.status == 204:
                    return True
    return False

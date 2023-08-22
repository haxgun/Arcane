import requests
from haxbod import settings


def existing_channel_twitch(channel_name: str) -> bool:
    client_id = settings.CLIENT_ID
    access_token = settings.ACCESS_TOKEN
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    url = f'https://api.twitch.tv/helix/users?login={channel_name}'
    response = requests.get(url, headers=headers)
    if response.ok and response.json().get('data'):
        return True
    return False

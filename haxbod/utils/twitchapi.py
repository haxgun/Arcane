import requests
from haxbod import settings


def existing_channel_twitch(channel_name):
    client_id = settings.CLIENT_ID
    access_token = settings.ACCESS_TOKEN

    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }

    url = f'https://api.twitch.tv/helix/users?login={channel_name}'

    response = requests.get(url, headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get('data'):
        return True
    else:
        return False

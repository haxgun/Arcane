import aiohttp

api_url = 'https://api.henrikdev.xyz'


async def fetch_data(url: str) -> dict | str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                return f'{response.status} - {response.reason}'


async def get_account_details(name_with_tag: str) -> dict | str:
    name, tag = name_with_tag.split('#')
    url = f'{api_url}/valorant/v1/account/{name}/{tag}'
    return await fetch_data(url)


async def get_puuid(name_with_tag: str) -> str:
    data = await get_account_details(name_with_tag)
    return data['data']['puuid'] if isinstance(data, dict) else data


async def get_region(name_with_tag: str) -> str:
    data = await get_account_details(name_with_tag)
    return data['data']['region'] if isinstance(data, dict) else data


async def get_account_level(name_with_tag: str) -> str:
    data = await get_account_details(name_with_tag)
    return data['data']['accountLevel'] if isinstance(data, dict) else data


async def get_mmr_details(name_with_tag: str) -> dict | str:
    affinity = await get_region(name_with_tag)
    puuid = await get_puuid(name_with_tag)
    url = f'{api_url}/valorant/v1/by-puuid/mmr/{affinity}/{puuid}'
    return await fetch_data(url)


async def get_rank_with_rr_and_elo(name_with_tag: str) -> str:
    name, tag = name_with_tag.split('#')
    data = await get_mmr_details(name_with_tag)
    if isinstance(data, dict):
        rank = data['data']['currenttierpatched']
        rr = data['data']['ranking_in_tier']
        elo = data['data']['elo']

        mmr_change = data['data']['mmr_change_to_last_game']
        if mmr_change > 0:
            mmr_change = '+' + str(mmr_change)

        return f'{rank} - {rr}RR - {elo} elo ({mmr_change}) - https://tracker.gg/valorant/profile/riot/{name}%23{tag}'
    else:
        return data


async def get_matches(name_with_tag: str, mode: str = 'competitive', size: int = None) -> dict | str:
    puuid = await get_puuid(name_with_tag)
    region = await get_region(name_with_tag)
    if size:
        url = f'{api_url}/valorant/v1/by-puuid/lifetime/matches/{region}/{puuid}?mode={mode}&size={size}'
    else:
        url = f'{api_url}/valorant/v1/by-puuid/lifetime/matches/{region}/{puuid}?mode={mode}&size=30'
    return await fetch_data(url)


async def get_stats_last_game(name_with_tag: str) -> dict | str:
    data = await get_matches(name_with_tag, size=1)
    game_data = data['data'][0]

    stats = game_data['stats']
    teams = game_data['teams']
    map_name = game_data['meta']['map']['name']
    match_id = game_data['meta']['id']
    team = game_data['stats']['team']

    character = stats['character']['name']
    kills = stats['kills']
    deaths = stats['deaths']
    assists = stats['assists']

    shots = stats['shots']
    head_shots = shots.get('head', 0)
    body_shots = shots.get('body', 0)
    leg_shots = shots.get('leg', 0)

    total_shots = head_shots + body_shots + leg_shots

    head_shot_percentage = round((head_shots / total_shots) * 100) if total_shots > 0 else 0

    red_score = teams['red']
    blue_score = teams['blue']

    if red_score > blue_score:
        win = 'Red'
    elif red_score < blue_score:
        win = 'Blue'
    else:
        win = 'Drew'

    if team == win:
        win_status = 'W'
    elif win == 'Drew':
        win_status = 'D'
    else:
        win_status = 'L'

    return (f'{map_name} [{win_status}] - {character} - {kills}/{deaths}/{assists} - HS: {head_shot_percentage}% - '
            f'https://tracker.gg/valorant/match/{match_id}')

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
    data = await get_mmr_details(name_with_tag)
    if isinstance(data, dict):
        rank = data['data']['currenttierpatched']
        rr = data['data']['ranking_in_tier']
        elo = data['data']['elo']
        return f'{rank} - {rr}RR - {elo} elo'
    else:
        return data

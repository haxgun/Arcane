# ⚗️ Arcane
[![GitHub License](https://img.shields.io/github/license/haxgun/Arcane)](https://github.com/haxgun/Arcane/blob/main/LICENSE)
![Python Version](https://img.shields.io/badge/Python-3.10+-informational.svg)

## ⚡️ Installation
**Required components:**
- Twitch Account for Bot
- Python 3.10+
- Pipenv or venv
- VSCode or Pycharm

To set up the Arcane, follow these steps:
1. Install [pipenv](https://pipenv.pypa.io/en/latest/).
2. Clone the repository
3. Install the necessary packages with `pipenv install`
4. Go to [TwitchTokenGenerator](https://twitchtokengenerator.com/) and generate initial token WITH ALL SCOPES.
5. Copy the example environment file: `cp .env.example .env` and update the variables with your prefix, database and Twitch credentials.
6. Add the channel to the database: `pipenv run addchannel`
7. Start using the bot: `pipenv run bot`

> **Note**
> If you want remove channel from database
> `pipenv run removechannel `

## 🗃️ Structure
* `/arcane`: main folder of the bot 
    * `/dataclasses`: dataclasses foler
    * `/extensions`: extensions folder
    * `/models`: models for Database
    * `/modules`: modules for bot
        * `/api`: API folder
    * `/settings`: configuration settings of the bot
    * `bot.py`: bot core
* `main.py`: main file for launch bot

## 📝 TODO
1. Learn more about the asyncio, aiohttp library
2. Add a separate class for connecting via a web socket and to different APIs

## 📄 License
[Arcane](https://github.com/haxgun/Arcane) is completely free and has an [the MIT license](https://github.com/haxgun/Arcane/blob/main/LICENSE). If you want, you can put a star on Github.

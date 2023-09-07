# ⚗️ Arcane
[![GitHub License](https://img.shields.io/github/license/haxgun/Arcane)](https://github.com/haxgun/Arcane/blob/main/LICENSE)
![Python Version](https://img.shields.io/badge/Python-3.11.4-informational.svg)
![TwitchIO Version](https://img.shields.io/badge/TwitchIO-2.6.0-informational.svg)

## ⚡️ Installation
**Required components:**
- Twitch Account for Bot
- Python 3.7+
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
    * `/cogs`: cogs folder
    * `/settings`: configuration settings of the bot
    * `/models`: modules for Database
    * `bot.py`: bot core
* `main.py`: main file for launch bot

## 📄 License
[Arcane](https://github.com/haxgun/Arcane) is completely free and has an [the MIT license](https://github.com/haxgun/Arcane/blob/main/LICENSE). If you want, you can put a star on Github.

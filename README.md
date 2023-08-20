<p></p>
<p align="center">
	<img width="300" src="docs/media/logo_dark.png#gh-light-mode-only"/>
	<img width="300" src="docs/media/logo_light.png#gh-dark-mode-only"/>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11.4-informational.svg">
  <img src="https://img.shields.io/badge/TwitchIO-2.6.0-informational.svg">
  <a href="https://github.com/starlitskies7/haxbod/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/starlitskies7/haxbod">
  </a>
</p>

---

## ⚡️ Installation
**Required components:**
- Twitch Account for Bot
- Python 3.11.4
- Pipenv or venv
- VSCode or Pycharm

To set up the Haxbod, follow these steps:
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
* `/haxbod`: main folder of the bot
    * `/cogs`: cogs folder
    * `/settings`: configuration settings of the bot
    * `/models`: modules for Database
    * `bot.py`: bot core
* `main.py`: main file for launch bot

## 📄 License
[Haxbot](https://github.com/starlitskies7/haxbod) is completely free and has an [the MIT license](https://github.com/starlitskies7/haxbod/blob/main/LICENSE). If you want, you can put a star on Github.

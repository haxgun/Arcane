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

> NOTE: I recommend using pipenv instead of venv

```bash
git clone https://github.com/starlitskies7/haxbod.git
cd haxbod

# Install the necessary packages

# If you use pipenv
pipenv install

# If you use venv
python -m venv .venv
# If you use Linux/MacOS
source .venv/bin/activate
# or if you use Windows
./venv/Scripts/activate
# For install packages
python -m pip install -r requirements.txt

# Go to https://twitchtokengenerator.com/
# Generate initial token WITH ALL SCOPES 

# Configure .env and rename
nano .env.example
cp .env.example .env

# Launch the bot

# If you use pipenv
pipenv run bot

# If you use venv
python main.py
```

## 📁 Structure

```bash
haxbod/
├── main.py                 # Main file for launch bot
├── docs                    # Files for docs
│   ├── media
│   │   ├── logo_dark.png   # Dark logo
│   │   ├── logo_light.png  # Light logo
├── haxbod                  # Main folder where the bot and its settings are contained
│   ├── cogs                # Cogs folder
│   │   ├── owner.py        # Owner cog with commands available only for owner bot
│   ├── settings        
│   │   ├── settings.py       # Config
│   │   ├── __init__.py
│   ├── models              # Modules for Database
│   │   ├── models.py       # Model Definitions
│   │   ├── __init__.py
│   ├── bot.py              # Main file for the bot to work
│   ├── __init__.py 
├── .env.example            # File for env settings
├── .gitignore              # .gitignore
├── LICENSE                 # License
├── README.md               # Readme
├── Pipfile                 # File with dependencies
└── requirements.txt        # File with dependencies
```
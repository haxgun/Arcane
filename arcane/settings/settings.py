import ast
from os import environ
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

dotenv_file = BASE_DIR / '.env'
if dotenv_file.is_file():
    load_dotenv(dotenv_file)

# Twitch Bot Settings
ACCESS_TOKEN = environ['ACCESS_TOKEN']
CLIENT_ID = environ['CLIENT_ID']

# Broadcaster Settings
BROADCASTER_TOKEN = environ['BROADCASTER_TOKEN']
BROADCASTER_CLIENT_ID = environ['BROADCASTER_CLIENT_ID']

# Bot settings
DEBUG = ast.literal_eval(environ['DEBUG'])
PREFIX = environ['PREFIX']
OWNER_ID = str(environ['OWNER_ID'])

# DB settings
DB_NAME = environ['DB_NAME']

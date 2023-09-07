from os import environ
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

dotenv_file = BASE_DIR / '.env'
if dotenv_file.is_file():
    load_dotenv(dotenv_file)

# Twitch Bot Token
ACCESS_TOKEN = environ['ACCESS_TOKEN']
REFRESH_TOKEN = environ['REFRESH_TOKEN']
CLIENT_ID = environ['CLIENT_ID']

# Bot settings
DEBUG = environ['DEBUG']
PREFIX = environ['PREFIX']
OWNER_ID = environ['OWNER_ID']

# DB settings
DB_NAME = environ['DB_NAME']

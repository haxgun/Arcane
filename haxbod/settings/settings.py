import os
import dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

dotenv_file = BASE_DIR / '.env'
if dotenv_file.is_file():
    dotenv.load_dotenv(dotenv_file)

ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
REFRESH_TOKEN = os.environ['REFRESH_TOKEN']
CLIENT_ID = os.environ['CLIENT_ID']

PREFIX = os.environ['PREFIX']
OWNER_ID = os.environ['OWNER_ID']

DB_NAME = os.environ['DB_NAME']

import json
import os

from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URI = os.getenv("DATABASE_URI")

CHECK_INTERVAL_SECONDS = float(os.getenv("CHECK_INTERVAL_SECONDS"))
SESSIONS_PATH = "./sessions/"
ACCOUNTS_FILE = os.getenv("ACCOUNTS_FILE")

with open(ACCOUNTS_FILE, encoding="utf-8") as f:
    ACCOUNTS = json.load(f)

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8846635582:AAEbEePqz_nYZDK7i0ypRiwG1b0zK3jl6Jo")

SUPPORT_CHAT_ID = int(os.getenv("SUPPORT_CHAT_ID", "7309670627"))

# Список адмінів
admin_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x) for x in admin_raw.split(",") if x.strip().isdigit()] if admin_raw else [7309670627]

SITE_URL = os.getenv("SITE_URL", "https://lololoi.github.io/LoveCoffee/")
DB_PATH = os.getenv("DB_PATH", "support_bot.db")
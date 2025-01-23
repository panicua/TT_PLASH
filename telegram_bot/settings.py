from decouple import config, Csv
# from TT_PLASH.settings import ALLOWED_HOSTS
import os
import sys
from django.conf import settings
from django import setup
from TT_PLASH.settings import DATABASES, ALLOWED_HOSTS
import dj_database_url

# TELEGRAM
BOT_TOKEN = config("TELEGRAM_BOT_API_TOKEN", default="")
BOT_ADMIN_IDS = config("TELEGRAM_ADMIN_IDS", cast=Csv(int), default=[])
BOT_OWNER_NAME = config("TELEGRAM_BOT_OWNER_USERNAME")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASES_URL = config("DATABASE_URL", default="sqlite:///../db.sqlite3")
settings.configure(
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'todo',
    ),
    DATABASES={"default": dj_database_url.parse(DATABASES_URL)},
)
setup()

API_SERVER_URL = ALLOWED_HOSTS[1]
if API_SERVER_URL == "127.0.0.1":
    API_SERVER_URL = "http://127.0.0.1:8000"

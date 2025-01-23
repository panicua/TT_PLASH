# from TT_PLASH.settings import ALLOWED_HOSTS
import os
import sys

import dj_database_url
from decouple import config, Csv
from django import setup
from django.conf import settings

from TT_PLASH.settings import ALLOWED_HOSTS

# TELEGRAM
BOT_TOKEN = config("TELEGRAM_BOT_API_TOKEN", default="")
BOT_ADMIN_IDS = config("TELEGRAM_ADMIN_IDS", cast=Csv(int), default=[])
BOT_OWNER_NAME = config("TELEGRAM_BOT_OWNER_USERNAME")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASES_URL = config("DATABASE_URL", default="sqlite:///../db.sqlite3")
settings.configure(
    INSTALLED_APPS=(
        "django.contrib.contenttypes",
        "todo",
    ),
    DATABASES={"default": dj_database_url.parse(DATABASES_URL)},
)
setup()

API_SERVER_URL = config("HOST_API_URL", default="http://telegram-plash-app:8000/")

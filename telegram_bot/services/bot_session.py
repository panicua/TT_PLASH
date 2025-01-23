from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

from telegram_bot.settings import BOT_TOKEN

session = AiohttpSession()

bot_instance = Bot(token=BOT_TOKEN, session=session)

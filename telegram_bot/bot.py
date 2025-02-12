from aiogram import Dispatcher

from telegram_bot.handlers import start, help, user, domain, todo
from telegram_bot.services.bot_session import bot_instance


async def main():
    telegram_bot = bot_instance
    dp = Dispatcher()

    dp.include_router(start.start_router)
    dp.include_router(help.help_router)
    dp.include_router(user.user_router)
    dp.include_router(domain.domain_router)
    dp.include_router(todo.todo_router)

    await dp.start_polling(telegram_bot)

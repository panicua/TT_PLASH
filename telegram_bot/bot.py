from aiogram import Dispatcher

from telegram_bot.handlers import start, help, user
from telegram_bot.services.bot_session import bot_instance


async def main():
    telegram_bot = bot_instance
    dp = Dispatcher()

    dp.include_router(start.start_router)
    dp.include_router(help.help_router)
    dp.include_router(user.user_router)

    dp.callback_query.register(user.process_delete_user_callback,
                               lambda c: c.data and c.data.startswith(
                                   'delete_user:'))

    dp.callback_query.register(user.process_edit_user_callback,
                               lambda c: c.data and c.data.startswith(
                                   'edit_user:'))

    dp.callback_query.register(user.process_change_group_callback,
                               lambda c: c.data and c.data.startswith(
                                   'change_group:'))

    dp.callback_query.register(user.process_delete_group_callback,
                               lambda c: c.data and c.data.startswith(
                                   'delete_group:'))

    await dp.start_polling(telegram_bot)

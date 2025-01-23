from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from asgiref.sync import sync_to_async

from telegram_bot.settings import BOT_ADMIN_IDS, BOT_OWNER_NAME
from todo.models import TelegramUser

start_router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    get_user_from_db = await sync_to_async(TelegramUser.objects.filter)(
        telegram_id=message.from_user.id, is_user=True
    )

    if message.from_user.id in BOT_ADMIN_IDS:
        user = await sync_to_async(get_user_from_db.first)()
        if not user:
            user = await sync_to_async(TelegramUser.objects.create)(
                telegram_id=message.from_user.id, is_admin=True, is_user=True
            )
        if not user.is_admin:
            user.is_admin = True
            await sync_to_async(user.save)()

        await message.reply(
            f"Hello, {message.from_user.first_name}! You got an admin access. Use /help to see commands.",
            reply_markup=ReplyKeyboardRemove(),
        )

    elif await sync_to_async(get_user_from_db.exists)():
        await message.reply(
            f"Hello, {message.from_user.first_name}! You got a user access. Use /help to see commands.",
            reply_markup=ReplyKeyboardRemove(),
        )

    else:
        await message.reply(
            f"Your id: {message.from_user.id}\n"
            f"You don't have access to use this bot yet. "
            f"Owner contact: {BOT_OWNER_NAME}\n",
            reply_markup=ReplyKeyboardRemove(),
        )

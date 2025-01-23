from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async

from todo.models import TelegramUser

help_router = Router()


@help_router.message(Command("help"))
async def command_help(message):
    get_user_from_db = await sync_to_async(TelegramUser.objects.filter)(
        telegram_id=message.from_user.id
    )

    if not await sync_to_async(get_user_from_db.exists)():
        await message.reply("You need to get an access first")
        return

    user = await sync_to_async(get_user_from_db.first)()
    if user.is_admin:
        await message.reply(
            "Users handling commands:\n"
            "/add-user      -> to add new user and group\n"
            "/delete-user   -> to delete user\n"
            "/edit-user     -> to edit user group\n"
            "\n"
            "Domain commands:\n"
            "/search        -> to check domains availability\n"
            "\n"
            "Todo commands:\n"
            "/create-todo   -> to create new todo with description\n"
            "/get-all-todo  -> to get all todos with short description and id\n"
            "/get-todo      -> to get todo by id\n"
            "/update-todo   -> to update todo description by id\n"
            "/delete-todo   -> to delete todo by id\n"
        )
    elif user.is_user:
        await message.reply(
            "Domain commands:\n"
            "/search        -> to check domains availability\n"
            "\n"
            "Todo commands:\n"
            "/create-todo   -> to create new todo with description\n"
            "/get-all-todo  -> to get all todos with short description and id\n"
            "/get-todo      -> to get todo by id\n"
            "/update-todo   -> to update todo description by id\n"
            "/delete-todo   -> to delete todo by id\n"
        )

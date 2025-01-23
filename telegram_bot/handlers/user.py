from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from todo.models import TelegramUser

user_router = Router()


class AddUser(StatesGroup):
    user_info = State()


async def is_admin(message: Message) -> bool:
    get_admin_from_db = await sync_to_async(TelegramUser.objects.filter)(
        telegram_id=message.from_user.id, is_admin=True
    )
    return await sync_to_async(get_admin_from_db.exists)()


@user_router.message(Command("add-user"))
async def command_add_user(message: Message, state: FSMContext):
    if await is_admin(message):
        await state.set_state(AddUser.user_info)
        await message.reply("Enter user id and group (optional)\nExample: 123456789;test_group")
    else:
        await message.reply("You are not an admin")


@user_router.message(Command("delete-user"))
async def command_delete_user(message: Message, state: FSMContext):
    if await is_admin(message):
        await message.reply("Enter user id")
    else:
        await message.reply("You are not an admin")


@user_router.message(AddUser.user_info)
async def get_user_info(message: Message, state: FSMContext):
    user_info = message.text.split(";")
    user_id = user_info[0]

    if not user_id.isnumeric():
        await message.reply("Invalid user id")
        return

    if len(user_info) > 1:
        user_group = user_info[1]
    else:
        user_group = None

    new_user = await sync_to_async(TelegramUser.objects.create)(
        telegram_id=user_id, group=user_group, is_user=True
    )
    await message.reply(f"New user created")

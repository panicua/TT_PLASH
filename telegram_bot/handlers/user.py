from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from telegram_bot.services.bot_session import bot_instance

from todo.models import TelegramUser

user_router = Router()


class AddUser(StatesGroup):
    user_info = State()


@sync_to_async
def is_admin_sync(message: Message) -> bool:
    return TelegramUser.objects.filter(telegram_id=message.from_user.id, is_admin=True).exists()


async def is_admin(message: Message) -> bool:
    return await is_admin_sync(message)


@sync_to_async
def get_user_ids_sync() -> list[int]:
    get_users_from_db = TelegramUser.objects.filter(is_user=True)
    return [user.telegram_id for user in get_users_from_db.all() if not user.is_admin]


async def get_user_ids() -> list[int]:
    return await get_user_ids_sync()


async def delete_user_from_db(user_id: int) -> None:
    user = await sync_to_async(TelegramUser.objects.filter)(telegram_id=user_id)
    await sync_to_async(user.delete)()


async def delete_user_group(user_id: int) -> None:
    user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
    user.group = None
    await sync_to_async(user.save)()


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
        user_ids = await get_user_ids()
        keyboard_buttons = [
            [InlineKeyboardButton(text=str(user_id),
                                  callback_data=f"delete_user:{user_id}")]
            for user_id in user_ids
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await message.reply("Select user id to delete:", reply_markup=keyboard)
    else:
        await message.reply("You are not an admin")


@user_router.message(Command("edit-user"))
async def command_edit_user(message: Message, state: FSMContext):
    if await is_admin(message):
        user_ids = await get_user_ids()
        keyboard_buttons = [[
                InlineKeyboardButton(text=str(user_id), callback_data=f"edit_user:{user_id}")
            ] for user_id in user_ids]
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await message.reply("Select user id to edit:", reply_markup=keyboard)
    else:
        await message.reply("You are not an admin")


async def process_edit_user_callback(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split(':')[1])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Change user group", callback_data=f"change_group:{user_id}")],
        [InlineKeyboardButton(text="Delete user group", callback_data=f"delete_group:{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"User {user_id} selected. Choose an action:", reply_markup=keyboard)
    await bot_instance.send_message(callback_query.from_user.id, f"User id: {user_id}")


async def process_delete_user_callback(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split(':')[1])
    await delete_user_from_db(user_id)
    await callback_query.answer(f"User {user_id} deleted")
    await bot_instance.send_message(callback_query.from_user.id, f"User {user_id} has been removed from the database.")


async def process_delete_group_callback(callback_query: types.CallbackQuery):
    user_id = int(callback_query.data.split(':')[1])
    await delete_user_group(user_id)
    await callback_query.message.edit_text(f"Group deleted for user {user_id}")
    await callback_query.answer()


async def process_change_group_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split(':')[1])
    await state.update_data(user_id=user_id)
    await state.set_state(AddUser.user_info)
    await callback_query.message.edit_text("Enter the new group for user:")


@user_router.message(AddUser.user_info)
async def get_user_info(message: Message, state: FSMContext):
    user_info = message.text.split(";")
    user_data = await state.get_data()
    if user_data:
        user_id = user_data['user_id']
        user_group = user_info[0]

        user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
        user.group = user_group
        await sync_to_async(user.save)()
        await message.reply(f"User {user_id} updated")
    else:
        user_id = user_info[0]
        if not user_id.isnumeric():
            await message.reply("Invalid user id")
            return

        if len(user_info) > 1:
            user_group = user_info[1]
        else:
            user_group = None

        await sync_to_async(TelegramUser.objects.create)(
            telegram_id=user_id, group=user_group, is_user=True
        )
        await message.reply(f"New user created")

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from asgiref.sync import sync_to_async

from todo.models import TelegramUser

user_router = Router()


class AddUser(StatesGroup):
    user_info = State()


class AddGroup(StatesGroup):
    user_info = State()


@sync_to_async
def is_admin_sync(message: Message) -> bool:
    return TelegramUser.objects.filter(
        telegram_id=message.from_user.id, is_admin=True
    ).exists()


async def is_admin(message: Message) -> bool:
    return await is_admin_sync(message)


@sync_to_async
def get_user_ids_sync() -> list[int]:
    get_users_from_db = TelegramUser.objects.filter(is_user=True)
    return [
        user.telegram_id for user in get_users_from_db.all() if not user.is_admin
    ]


async def get_user_ids() -> list[int]:
    return await get_user_ids_sync()


async def delete_user_from_db(user_id: int) -> None:
    user = await sync_to_async(TelegramUser.objects.filter)(telegram_id=user_id)
    await sync_to_async(user.delete)()


async def delete_user_group(user_id: int) -> None:
    user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
    user.group = None
    await sync_to_async(user.save)()


def create_keyboard(
    buttons: list[list[InlineKeyboardButton]],
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@user_router.message(Command("add-user"))
async def command_add_user(message: Message, state: FSMContext):
    if await is_admin(message):
        await state.set_state(AddUser.user_info)
        await message.reply(
            "Enter user id and group (optional)\nExample: 123456789;test_group"
        )
    else:
        await message.reply("You are not an admin")


@user_router.message(Command("delete-user"))
@user_router.message(Command("edit-user"))
async def command_handle_users(message: Message, state: FSMContext):
    if await is_admin(message):
        user_ids = await get_user_ids()
        command = message.text.strip("/")
        callback_data_prefix = f"{command}"
        keyboard_buttons = [
            [
                InlineKeyboardButton(
                    text=str(user_id),
                    callback_data=f"{callback_data_prefix.replace('-', '_')}:{user_id}",
                )
            ]
            for user_id in user_ids
        ]
        keyboard = create_keyboard(keyboard_buttons)
        await message.reply(
            f"Select user id to {command.replace('-', ' ')}:", reply_markup=keyboard
        )
    else:
        await message.reply("You are not an admin")


@user_router.callback_query(
    lambda c: c.data
    and (c.data.startswith("delete_user:") or c.data.startswith("edit_user:"))
)
async def process_user_callback(callback_query: CallbackQuery, state: FSMContext):
    action, user_id = callback_query.data.split(":")
    user_id = int(user_id)
    if action == "delete_user":
        await delete_user_from_db(user_id)
        await callback_query.message.edit_text(f"User {user_id} has been deleted.")
    elif action == "edit_user":
        keyboard = create_keyboard(
            [
                [
                    InlineKeyboardButton(
                        text="Delete group", callback_data=f"delete_group:{user_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Add new group", callback_data=f"add_group:{user_id}"
                    )
                ],
            ]
        )
        await callback_query.message.edit_text(
            f"User {user_id} selected. Choose an action:", reply_markup=keyboard
        )

    await callback_query.answer()


@user_router.callback_query(lambda c: c.data and c.data.startswith("add_group:"))
async def process_add_group_callback(
    callback_query: CallbackQuery, state: FSMContext
):
    user_id = int(callback_query.data.split(":")[1])
    await state.update_data(user_id=user_id)
    await state.set_state(AddGroup.user_info)
    await callback_query.message.edit_text("Enter the new group for user:")
    await callback_query.answer()


@user_router.callback_query(lambda c: c.data and c.data.startswith("delete_group:"))
async def process_delete_group_callback(
    callback_query: CallbackQuery, state: FSMContext
):
    user_id = int(callback_query.data.split(":")[1])
    await delete_user_group(user_id)
    await callback_query.message.edit_text(
        f"Group has been deleted from user {user_id}."
    )
    await callback_query.answer()


@user_router.message(AddGroup.user_info)
async def add_group_to_user(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    if not user_id:
        await message.reply("User ID not found in state.")
        return

    new_group = message.text

    user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
    user.group = new_group
    await sync_to_async(user.save)()

    await message.reply(f"Group '{new_group}' has been added to user {user_id}.")
    await state.clear()


@user_router.message(AddUser.user_info)
async def add_user(message: Message, state: FSMContext):
    user_info = message.text.split(";")
    user_id = user_info[0]
    group = user_info[1] if len(user_info) > 1 else None

    try:
        user = await sync_to_async(TelegramUser.objects.get)(telegram_id=user_id)
        await message.reply(f"User with ID {user_id} already exists.")
    except TelegramUser.DoesNotExist:
        user = TelegramUser(telegram_id=user_id, group=group, is_user=True)
        await sync_to_async(user.save)()
        await message.reply(
            f"User with ID {user_id} has been added with group '{group}'."
            if group
            else f"User with ID {user_id} has been added."
        )

    await state.clear()

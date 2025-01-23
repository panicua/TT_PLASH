import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from telegram_bot.handlers.user import is_user
from telegram_bot.services.constants import TELEGRAM_HEADERS
from telegram_bot.settings import API_SERVER_URL

todo_router = Router()


class TodoInfo(StatesGroup):
    description = State()


class TodoStates(StatesGroup):
    GET_TODO_ID = State()
    DELETE_TODO_ID = State()
    UPDATE_TODO_ID = State()


# Crete todo with description
@todo_router.message(Command("create-todo"))
async def command_create_todo(message: Message, state: FSMContext) -> None:
    if await is_user(message):
        await state.set_state(TodoInfo.description)
        await message.reply("Enter todo description:")
    else:
        await message.reply("You are not a user")
        return


async def create_todo_api(message: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_SERVER_URL}/api/todo/",
            json={"description": message},
            headers=TELEGRAM_HEADERS,
        ) as response:
            if response.status == 201:
                return await response.json()
            else:
                raise Exception("Failed to create todo")


@todo_router.message(TodoInfo.description)
async def create_todo_handler(message: Message, state: FSMContext) -> None:
    todo_description = message.text
    try:
        await create_todo_api(todo_description)
        if len(todo_description) > 20:
            todo_description = f"{todo_description[:20]}..."
        await message.reply(f"Todo '{todo_description}' has been created.")
    except Exception as e:
        await message.reply(f"Failed to create todo: {e}")
    finally:
        await state.clear()


# get single todo
@todo_router.message(Command("get-todo"))
async def command_get_todo_handler(message: Message, state: FSMContext) -> None:
    if await is_user(message):
        await message.reply("Enter the ID of the todo:")
        await state.set_state(TodoStates.GET_TODO_ID)
    else:
        await message.reply("You are not a user")
        return


@todo_router.message(TodoStates.GET_TODO_ID, lambda message: message.text.isdigit())
async def get_todo_handler(message: Message, state: FSMContext) -> None:
    todo_id = message.text
    try:
        todo = await get_todo_api(todo_id)
        await message.reply(
            f"Todo ID: {todo['id']}\nDescription: {todo['description']}"
        )
    except Exception as e:
        await message.reply(f"Failed to get todo: {e}")
    finally:
        await state.clear()


async def get_todo_api(todo_id: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_SERVER_URL}/api/todo/{todo_id}/", headers=TELEGRAM_HEADERS
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception("Failed to get todo")


# get all todos
@todo_router.message(Command("get-all-todo"))
async def command_get_all_todo_handler(message: Message) -> None:
    if await is_user(message):
        pass
    else:
        await message.reply("You are not a user")
        return

    try:
        todos = await get_all_todo_api()
        print(todos)
        todos_list = "\n".join(
            [
                f"ID: {todo['id']}, "
                f"Description: {todo['description'] if len(todo['description']) < 30 else todo['description'][:30] + '...'}"
                for todo in todos
            ]
        )
        await message.reply(f"All ToDos:\n{todos_list}")
    except Exception as e:
        await message.reply(f"Failed to get all todos: {e}")


async def get_all_todo_api() -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_SERVER_URL}/api/todo/", headers=TELEGRAM_HEADERS
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception("Failed to get all todos")


# update todo
@todo_router.message(Command("update-todo"))
async def command_update_todo_handler(message: Message, state: FSMContext) -> None:
    if await is_user(message):
        await message.reply(
            "Enter the ID of the todo and the new description separated by ';' Example: 1;New description"
        )
        await state.set_state(TodoStates.UPDATE_TODO_ID)
    else:
        await message.reply("You are not a user")
        return


@todo_router.message(TodoStates.UPDATE_TODO_ID, lambda message: ";" in message.text)
async def update_todo_handler(message: Message, state: FSMContext) -> None:
    try:
        todo_id, new_description = map(str.strip, message.text.split(";", 1))
        await update_todo_api(todo_id, new_description)
        await message.reply("Todo updated successfully!")
    except Exception as e:
        await message.reply(f"Failed to update todo: {e}")
    finally:
        await state.clear()


async def update_todo_api(todo_id: str, description: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{API_SERVER_URL}/api/todo/{todo_id}/",
            json={"description": description},
            headers=TELEGRAM_HEADERS,
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception("Failed to update todo")


# delete todo
@todo_router.message(Command("delete-todo"))
async def command_delete_todo_handler(message: Message, state: FSMContext) -> None:
    if await is_user(message):
        await message.reply("Enter the ID of the todo to delete:")
        await state.set_state(TodoStates.DELETE_TODO_ID)
    else:
        await message.reply("You are not a user")
        return


@todo_router.message(
    TodoStates.DELETE_TODO_ID, lambda message: message.text.isdigit()
)
async def delete_todo_handler(message: Message, state: FSMContext) -> None:
    todo_id = message.text
    try:
        await delete_todo_api(todo_id)
        await message.reply("Todo deleted successfully!")
    except Exception as e:
        await message.reply(f"Failed to delete todo: {e}")
    finally:
        await state.clear()


async def delete_todo_api(todo_id: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            f"{API_SERVER_URL}/api/todo/{todo_id}/", headers=TELEGRAM_HEADERS
        ) as response:
            if response.status == 204:
                return
            else:
                raise Exception("Failed to delete todo")

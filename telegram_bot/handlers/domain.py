import aiohttp
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from telegram_bot.handlers.user import is_user

domain_router = Router()


class Search(StatesGroup):
    domains = State()


@domain_router.message(Command("search"))
async def command_search(message: Message, state: FSMContext):
    if await is_user(message):
        await state.set_state(Search.domains)
        await message.reply(
            "Enter domains name to check availability\n"
            "Example:\nhttps://google.com\nfacebook.com\nhttp://youtube.com\ngithub.com"
        )
    else:
        await message.reply("You are not a user")
        return


@domain_router.message(Search.domains)
async def handle_domains_input(message: Message, state: FSMContext):
    domains = message.text.split()
    print(domains)
    results = []

    async with aiohttp.ClientSession() as session:
        for domain in domains:
            if not domain.startswith("http://") and not domain.startswith(
                "https://"
            ):
                domain = "https://" + domain

            result = f"Domain: {domain}\n"
            ssl_status = "Not checked"
            status_code = "Not checked"
            availability = "Unavailable"

            try:
                async with session.get(domain, ssl=True) as response:
                    ssl_status = (
                        "OK" if response.url.scheme == "https" else "Нет SSL"
                    )
                    status_code = response.status
                    availability = (
                        "Available" if response.status == 200 else "Недоступен"
                    )
            except Exception as e:
                ssl_status = "Error"
                status_code = f"Error: {e}"

            result += f"- SSL: {ssl_status}\n"
            result += f"- Status: {status_code}\n"
            result += f"- Availability: {availability}\n"
            results.append(result)

    await message.reply("\n\n".join(results))
    await state.clear()

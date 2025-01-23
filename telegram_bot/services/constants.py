from decouple import config


TELEGRAM_HEADERS = {
    "Content-Type": "application/json",
    "X-Telegram-Secret": config("TELEGRAM_SECRET_HEADER_TOKEN"),
}

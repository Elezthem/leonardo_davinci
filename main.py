import asyncio
from aiogram import Bot, Dispatcher

import handlers

from data.databases import DataBase


async def main() -> None:
    bot = Bot("6603429920:AAGgQdIRgUDWzZgdwGLX-CSVqrKJSPlL3Y0")
    dp = Dispatcher()
    db = DataBase()

    dp.startup.register(db.create) # Создаем БД при запуске бота.
    dp.include_routers(
        handlers.questrionaire.router,
        handlers.bot_messages.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, db=db)


if __name__ == "__main__":
    asyncio.run(main())
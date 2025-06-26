import os
import handlers
from aiogram import executor, types
from data import config
from loader import dp, db, bot
import filters
import logging
from utils.bot_commands import set_default_commands
from handlers.user.menu import admin_menu, user_menu
from states.register_state import Register

filters.setup(dp)

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer("👋 Assalomu alaykum.\n\nBotga xush kelibsiz!")

    user = db.get_user(message.from_user.id)
    if user:
        if message.from_user.id in config.ADMINS:
            await admin_menu(message)
        else:
            await user_menu(message)
    else:
        await message.answer("Ro'yxatdan o'tish uchun ismingizni kiriting:")
        await Register.name.set()


async def on_startup(dp):
    logging.basicConfig(level=logging.INFO)
    db.create_tables()

    # Set up bot commands
    await set_default_commands(dp)

    await bot.delete_webhook()
    if config.WEBHOOK_URL:
        await bot.set_webhook(config.WEBHOOK_URL)


async def on_shutdown():
    logging.warning("Shutting down..")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")


if __name__ == "__main__":

    if ("HEROKU_APP_NAME" in list(os.environ.keys())) or (
        "RAILWAY_PUBLIC_DOMAIN" in list(os.environ.keys())
    ):

        executor.start_webhook(
            dispatcher=dp,
            webhook_path=config.WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )

    else:

        executor.start_polling(dp, on_startup=on_startup, skip_updates=False)

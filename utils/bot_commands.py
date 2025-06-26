from aiogram.types import BotCommand


async def set_default_commands(dp):
    """
    Set default bot commands in the Telegram client
    """
    await dp.bot.set_my_commands(
        [
            BotCommand("start", "🚀 Botni boshlash"),
            BotCommand("menu", "📜 Bosh menuni ochish"),
            BotCommand("sos", "🆘 Adminga murojaat"),
        ]
    )

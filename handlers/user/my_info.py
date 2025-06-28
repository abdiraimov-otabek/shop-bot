from aiogram.types import Message, ReplyKeyboardMarkup
from loader import dp, db
from filters import IsUser
from .menu import my_info


@dp.message_handler(IsUser(), text=my_info)
async def process_my_info(message: Message):
    # Get user information from database
    user_data = db.get_user(message.chat.id)

    if user_data:
        cid, name, phone_number, balance = user_data
        await message.answer(
            f"Sizning ma'lumotlaringiz:\n\n"
            f"👤 Ismingiz: {name}\n"
            f"📞 Telefon raqamingiz: +{phone_number}\n"
            f"💰 Balansingiz: {balance} so'm"
        )
    else:
        await message.answer("Ma'lumot topilmadi. Iltimos, qaytadan ro'yxatdan o'ting.")

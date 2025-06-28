from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from loader import dp
from filters import IsAdmin, IsUser

# User menu items
catalog = "🛍 Buyurtma berish"
cart = "🗂 Savat"
orders = "✍️ Buyurtmalar"
purchases = "💵 Xaridlar"
my_info = "📝 Mening ma'lumotlarim"
balance = "💰 Hozirgi balans"
delivery_status = "🎚️ Buyurtma statusi"
questions = "❓ Savollar"

# Admin menu items
admin_settings = "⚙️ Katalogni sozlash"
admin_orders = "🚚 Buyurtmalar"
admin_questions = "❓ Savollar"


@dp.message_handler(IsAdmin(), commands="menu")
async def admin_menu(message: Message):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(admin_settings)
    markup.add(admin_questions, admin_orders)

    await message.answer("Bosh menyu", reply_markup=markup)


@dp.message_handler(IsUser(), commands="menu")
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(catalog)
    markup.add(cart, orders)
    markup.add(purchases, balance)
    markup.add(my_info)

    await message.answer("Bosh menyu", reply_markup=markup)

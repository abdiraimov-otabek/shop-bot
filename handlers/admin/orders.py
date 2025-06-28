from aiogram.types import Message
from loader import dp, db
from handlers.user.menu import admin_orders
from filters import IsAdmin


@dp.message_handler(IsAdmin(), text=admin_orders)
async def process_orders(message: Message):

    orders = db.fetchall("SELECT * FROM orders")

    if len(orders) == 0:
        await message.answer("Sizda hech qanday buyurtma yo'q.")
    else:
        await order_answer(message, orders)


async def order_answer(message, orders):

    res = ""

    for i, order in enumerate(orders, 1):
        print(order)
        customer_id, customer_name, address, products = order

        res += f"📦 <b>Buyurtma #{i}</b>\n"
        res += f"👤 <b>Mijoz:</b> {customer_name}\n"
        res += f"🆔 <b>ID:</b> {customer_id}\n"
        res += f"📍 <b>Manzil:</b> {address}\n"
        res += f"🛍️ <b>Mahsulotlar:</b> {products}\n"
        res += f"{'─' * 30}\n\n"

    await message.answer(res)

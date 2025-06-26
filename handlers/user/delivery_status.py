from aiogram.types import Message
from loader import dp, db
from .menu import delivery_status
from filters import IsUser


@dp.message_handler(IsUser(), text=delivery_status)
async def process_delivery_status(message: Message):

    orders = db.fetchall("SELECT * FROM orders WHERE cid=?", (message.chat.id,))

    if len(orders) == 0:
        await message.answer("Sizda aktiv buyurtmalar yo'q.")
    else:
        await delivery_status_answer(message, orders)


async def delivery_status_answer(message, orders):

    res = ""

    for order in orders:

        res += f"Buyurtma <b>№{order[3]}</b>"
        answer = [" omborda.", " yo'lda!", " yetib keldi va sizni pochtada kutmoqda!"]

        res += answer[0]
        res += "\n\n"

    await message.answer(res)

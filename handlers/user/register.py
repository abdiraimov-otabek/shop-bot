from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentType, ReplyKeyboardMarkup
from loader import dp, db
from states.register_state import Register
from handlers.user.menu import user_menu
from keyboards.default.markups import send_contact


@dp.message_handler(state=Register.name)
async def process_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text

    await Register.next()
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=send_contact())


@dp.message_handler(
    content_types=[ContentType.CONTACT, ContentType.TEXT], state=Register.phone_number
)
async def process_phone_number(message: Message, state: FSMContext):
    async with state.proxy() as data:
        if message.contact:
            data["phone_number"] = message.contact.phone_number
        else:
            data["phone_number"] = message.text

        cid = message.chat.id
        name = data["name"]
        phone_number = data["phone_number"]

        db.add_user(cid, name, phone_number)

    await state.finish()

    # Create user menu markup
    markup = ReplyKeyboardMarkup(selective=True)
    from handlers.user.menu import (
        catalog,
        cart,
        orders,
        purchases,
        balance,
        my_info,
    )

    markup.add(catalog)
    markup.add(cart, orders)
    markup.add(purchases, balance)
    markup.add(my_info)

    await message.answer("Rahmat! Ro'yxatdan o'tdingiz.", reply_markup=markup)

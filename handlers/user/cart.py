import logging
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from keyboards.inline.products_from_cart import product_markup, product_cb
from aiogram.utils.callback_data import CallbackData
from keyboards.default.markups import *
from aiogram.types.chat import ChatActions
from states import CheckoutState
from loader import dp, db, bot
from filters import IsUser
from .menu import cart


@dp.message_handler(IsUser(), text=cart)
async def process_cart(message: Message, state: FSMContext):

    cart_data = db.fetchall("SELECT * FROM cart WHERE cid=%s", (message.chat.id,))

    if len(cart_data) == 0:

        await message.answer("Savatingiz bo'sh.")

    else:

        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        async with state.proxy() as data:
            data["products"] = {}

        order_cost = 0

        for _, idx, count_in_cart in cart_data:

            product = db.fetchone("SELECT * FROM products WHERE idx=%s", (idx,))

            if product == None:

                db.query("DELETE FROM cart WHERE idx=%s", (idx,))

            else:
                _, title, body, image, price, _ = product
                order_cost += price

                async with state.proxy() as data:
                    data["products"][idx] = [title, price, count_in_cart]

                markup = product_markup(idx, count_in_cart)
                text = f"<b>{title}</b>\n\n{body}\n\nNarxi: {price} so'm"

                await message.answer_photo(
                    photo=image, caption=text, reply_markup=markup
                )

        if order_cost != 0:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup = back_markup()
            markup.add("📦 Buyurtma berish")

            await message.answer(
                "Buyurtma berishga o'tishni xohlaysizmi?", reply_markup=markup
            )


@dp.callback_query_handler(IsUser(), product_cb.filter(action="count"))
@dp.callback_query_handler(IsUser(), product_cb.filter(action="increase"))
@dp.callback_query_handler(IsUser(), product_cb.filter(action="decrease"))
async def product_callback_handler(
    query: CallbackQuery, callback_data: dict, state: FSMContext
):

    idx = callback_data["id"]
    action = callback_data["action"]

    if "count" == action:

        async with state.proxy() as data:

            if "products" not in data.keys():

                await process_cart(query.message, state)

            else:

                await query.answer("Miqdori - " + data["products"][idx][2])

    else:

        async with state.proxy() as data:

            if "products" not in data.keys():

                await process_cart(query.message, state)

            else:

                data["products"][idx][2] += 1 if "increase" == action else -1
                count_in_cart = data["products"][idx][2]

                if count_in_cart == 0:

                    db.query(
                        """DELETE FROM cart
                    WHERE cid = %s AND idx = %s""",
                        (query.message.chat.id, idx),
                    )

                    await query.message.delete()
                else:

                    db.query(
                        """UPDATE cart 
                    SET quantity = %s 
                    WHERE cid = %s AND idx = %s""",
                        (count_in_cart, query.message.chat.id, idx),
                    )

                    await query.message.edit_reply_markup(
                        product_markup(idx, count_in_cart)
                    )


@dp.message_handler(IsUser(), text="📦 Buyurtma berish")
async def process_checkout(message: Message, state: FSMContext):

    await CheckoutState.check_cart.set()
    await checkout(message, state)


async def checkout(message, state):
    answer = ""
    total_price = 0

    async with state.proxy() as data:

        for title, price, count_in_cart in data["products"].values():

            tp = count_in_cart * price
            answer += f"<b>{title}</b> * {count_in_cart}sht. = {tp} so'm\n"
            total_price += tp

    await message.answer(
        f"{answer}\nUmumiy buyurtma summasi: {total_price} so'm.",
        reply_markup=check_markup(),
    )


@dp.message_handler(IsUser(), text="👈 Buyurtma berish")
async def back_to_menu(message: Message):
    await message.reply("🏠 Asosiy menuga qaytdingiz.", reply_markup=back_markup())


@dp.message_handler(
    IsUser(),
    lambda message: message.text not in [all_right_message, back_message],
    state=CheckoutState.check_cart,
)
async def process_check_cart_invalid(message: Message):
    await message.reply("Bunday variant yo'q.")


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.check_cart)
async def process_check_cart_back(message: Message, state: FSMContext):
    await state.finish()
    await process_cart(message, state)


@dp.message_handler(IsUser(), text=all_right_message, state=CheckoutState.check_cart)
async def process_check_cart_all_right(message: Message, state: FSMContext):
    await CheckoutState.next()
    await message.answer("Ismingizni kiriting.", reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.name)
async def process_name_back(message: Message, state: FSMContext):
    await CheckoutState.check_cart.set()
    await checkout(message, state)


@dp.message_handler(IsUser(), state=CheckoutState.name)
async def process_name(message: Message, state: FSMContext):

    async with state.proxy() as data:

        data["name"] = message.text

        if "address" in data.keys():

            await confirm(message)
            await CheckoutState.confirm.set()

        else:

            await CheckoutState.next()
            await message.answer("Manzilingizni kiriting.", reply_markup=back_markup())


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.address)
async def process_address_back(message: Message, state: FSMContext):

    async with state.proxy() as data:

        await message.answer(
            "Ismni <b>" + data["name"] + "</b> ga o'zgartirishni xohlaysizmi?",
            reply_markup=back_markup(),
        )

    await CheckoutState.name.set()


@dp.message_handler(IsUser(), state=CheckoutState.address)
async def process_address(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data["address"] = message.text

    await confirm(message)
    await CheckoutState.next()


async def confirm(message):

    await message.answer(
        "Barcha ma'lumotlar to'g'ri va buyurtmani tasdiqlangmi?",
        reply_markup=confirm_markup(),
    )


@dp.message_handler(
    IsUser(),
    lambda message: message.text not in [confirm_message, back_message],
    state=CheckoutState.confirm,
)
async def process_confirm_invalid(message: Message):
    await message.reply("Bunday variant yo'q.")


@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    await CheckoutState.address.set()

    async with state.proxy() as data:
        await message.answer(
            "Manzilni <b>" + data["address"] + "</b> ga o'zgartirishni xohlaysizmi?",
            reply_markup=back_markup(),
        )


@dp.message_handler(IsUser(), text=confirm_message, state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    enough_money = True  # enough money on the balance sheet
    markup = ReplyKeyboardRemove()

    if enough_money:

        logging.info("Deal was made.")

        async with state.proxy() as data:

            cid = message.chat.id
            products = [
                idx + "=" + str(quantity)
                for idx, quantity in db.fetchall(
                    """SELECT idx, quantity FROM cart
            WHERE cid=%s""",
                    (cid,),
                )
            ]  # idx=quantity

            db.query(
                "INSERT INTO orders VALUES (%s, %s, %s, %s)",
                (cid, data["name"], data["address"], " ".join(products)),
            )

            db.query("DELETE FROM cart WHERE cid=%s", (cid,))

            await message.answer(
                "✅ Buyurtmangiz yo'lga chiqdi! 🚀\nIsm: <b>"
                + data["name"]
                + "</b>\nManzil: <b>"
                + data["address"]
                + "</b>",
                reply_markup=markup,
            )
    else:

        await message.answer(
            "Hisobingizda mablag' yetarli emas. Hisobni to'ldiring!",
            reply_markup=markup,
        )

    await state.finish()

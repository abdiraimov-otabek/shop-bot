from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ContentType,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.callback_data import CallbackData
from keyboards.default.markups import *
from states import ProductState, CategoryState
from aiogram.types.chat import ChatActions
from handlers.user.menu import admin_settings
from loader import dp, db, bot
from filters import IsAdmin
from hashlib import md5


category_cb = CallbackData("category", "id", "action")
product_cb = CallbackData("product", "id", "action")

add_product = "➕ Mahsulot qo'shish"
delete_category = "🗑️ Kategoriyani o'chirish"


@dp.message_handler(IsAdmin(), text=admin_settings)
async def process_settings(message: Message):

    markup = InlineKeyboardMarkup()

    for idx, title in db.fetchall("SELECT * FROM categories"):

        markup.add(
            InlineKeyboardButton(
                title, callback_data=category_cb.new(id=idx, action="view")
            )
        )

    markup.add(
        InlineKeyboardButton("➕ Kategoriya qo'shish", callback_data="add_category")
    )

    await message.answer("⚙️ Kategoriyalarni sozlash:", reply_markup=markup)


@dp.callback_query_handler(IsAdmin(), category_cb.filter(action="view"))
async def category_callback_handler(
    query: CallbackQuery, callback_data: dict, state: FSMContext
):

    category_idx = callback_data["id"]

    products = db.fetchall(
        """SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=%s)""",
        (category_idx,),
    )

    await query.message.delete()
    await query.answer("📦 Ushbu kategoriyadagi barcha mahsulotlar.")
    await state.update_data(category_index=category_idx)
    await show_products(query.message, products, category_idx)


# category


@dp.callback_query_handler(IsAdmin(), text="add_category")
async def add_category_callback_handler(query: CallbackQuery):
    await query.message.delete()
    await query.message.answer("✍️ Kategoriya nomini kiriting:")
    await CategoryState.title.set()


@dp.message_handler(IsAdmin(), state=CategoryState.title)
async def set_category_title_handler(message: Message, state: FSMContext):

    category = message.text
    idx = md5(category.encode("utf-8")).hexdigest()
    db.query("INSERT INTO categories VALUES (%s, %s)", (idx, category))

    await state.finish()
    await process_settings(message)


@dp.message_handler(IsAdmin(), text=delete_category)
async def delete_category_handler(message: Message, state: FSMContext):

    async with state.proxy() as data:

        if "category_index" in data.keys():

            idx = data["category_index"]

            db.query(
                "DELETE FROM products WHERE tag IN (SELECT title FROM categories WHERE idx=%s)",
                (idx,),
            )
            db.query("DELETE FROM categories WHERE idx=%s", (idx,))

            await message.answer("✅ Bajarildi!", reply_markup=ReplyKeyboardRemove())
            await process_settings(message)


# add product


@dp.message_handler(IsAdmin(), text=add_product)
async def process_add_product(message: Message):

    await ProductState.title.set()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(cancel_message)

    await message.answer("✍️ Mahsulot nomini kiriting:", reply_markup=markup)


@dp.message_handler(IsAdmin(), text=cancel_message, state=ProductState.title)
async def process_cancel(message: Message, state: FSMContext):

    await message.answer("👌 Ok, bekor qilindi!", reply_markup=ReplyKeyboardRemove())
    await state.finish()

    await process_settings(message)


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.title)
async def process_title_back(message: Message, state: FSMContext):
    await process_add_product(message)


@dp.message_handler(IsAdmin(), state=ProductState.title)
async def process_title(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data["title"] = message.text

    await ProductState.next()
    await message.answer("📝 Mahsulot tavsifini kiriting:", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.body)
async def process_body_back(message: Message, state: FSMContext):

    await ProductState.title.set()

    async with state.proxy() as data:

        await message.answer(
            f"🤔 <b>{data['title']}</b> nomini o'zgartirasizmi?",
            reply_markup=back_markup(),
        )


@dp.message_handler(IsAdmin(), state=ProductState.body)
async def process_body(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data["body"] = message.text

    await ProductState.next()
    await message.answer("🖼️ Mahsulot rasmini yuboring:", reply_markup=back_markup())


@dp.message_handler(
    IsAdmin(), content_types=ContentType.PHOTO, state=ProductState.image
)
async def process_image_photo(message: Message, state: FSMContext):

    fileID = message.photo[-1].file_id
    file_info = await bot.get_file(fileID)
    downloaded_file = (await bot.download_file(file_info.file_path)).read()

    async with state.proxy() as data:
        data["image"] = downloaded_file

    await ProductState.next()
    await message.answer("💰 Narxini kiriting:", reply_markup=back_markup())


@dp.message_handler(IsAdmin(), content_types=ContentType.TEXT, state=ProductState.image)
async def process_image_url(message: Message, state: FSMContext):

    if message.text == back_message:

        await ProductState.body.set()

        async with state.proxy() as data:

            await message.answer(
                f"🤔 <b>{data['body']}</b> tavsifini o'zgartirasizmi?",
                reply_markup=back_markup(),
            )

    else:

        await message.answer("🖼️ Iltimos, mahsulot rasmini yuboring.")


@dp.message_handler(
    IsAdmin(), lambda message: not message.text.isdigit(), state=ProductState.price
)
async def process_price_invalid(message: Message, state: FSMContext):

    if message.text == back_message:

        await ProductState.image.set()

        async with state.proxy() as data:

            await message.answer(
                "🤔 Boshqa rasm yuborasizmi?", reply_markup=back_markup()
            )

    else:

        await message.answer("🔢 Narxni raqam bilan kiriting!")


@dp.message_handler(
    IsAdmin(), lambda message: message.text.isdigit(), state=ProductState.price
)
async def process_price(message: Message, state: FSMContext):

    async with state.proxy() as data:

        data["price"] = message.text

        title = data["title"]
        body = data["body"]
        price = data["price"]

        await ProductState.next()
        text = f"Nomi <b>{title}</b>Tavsifi\n\n{body}\n\n💰 Narxi: {price} so'm."

        markup = check_markup()

        await message.answer_photo(
            photo=data["image"], caption=text, reply_markup=markup
        )


@dp.message_handler(
    IsAdmin(),
    lambda message: message.text not in [back_message, all_right_message],
    state=ProductState.confirm,
)
async def process_confirm_invalid(message: Message, state: FSMContext):
    await message.answer("🤷‍♂️ Bunday variant mavjud emas.")


@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.confirm)
async def process_confirm_back(message: Message, state: FSMContext):

    await ProductState.price.set()

    async with state.proxy() as data:

        await message.answer(
            f"🤔 <b>{data['price']}</b> so'm narxini o'zgartirasizmi?",
            reply_markup=back_markup(),
        )


@dp.message_handler(IsAdmin(), text=all_right_message, state=ProductState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    async with state.proxy() as data:

        title = data["title"]
        body = data["body"]
        image = data["image"]
        price = data["price"]

        tag = db.fetchone(
            "SELECT title FROM categories WHERE idx=%s", (data["category_index"],)
        )[0]
        idx = md5(" ".join([title, body, price, tag]).encode("utf-8")).hexdigest()

        db.query(
            "INSERT INTO products VALUES (%s, %s, %s, %s, %s, %s)",
            (idx, title, body, image, int(price), tag),
        )

    await state.finish()
    await message.answer("✅ Bajarildi!", reply_markup=ReplyKeyboardRemove())
    await process_settings(message)


# delete product


@dp.callback_query_handler(IsAdmin(), product_cb.filter(action="delete"))
async def delete_product_callback_handler(query: CallbackQuery, callback_data: dict):

    product_idx = callback_data["id"]
    db.query("DELETE FROM products WHERE idx=%s", (product_idx,))
    await query.answer("🗑️ O'chirildi!")
    await query.message.delete()


async def show_products(m, products, category_idx):

    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)

    for idx, title, body, image, price, tag in products:

        text = f"<b>{title}</b>\n\n{body}\n\n💰 Narxi: {price} so'm."

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "🗑️ O'chirish", callback_data=product_cb.new(id=idx, action="delete")
            )
        )

        await m.answer_photo(photo=image, caption=text, reply_markup=markup)

    markup = ReplyKeyboardMarkup()
    markup.add(add_product)
    markup.add(delete_category)

    await m.answer(
        "❓ Biror narsa qo'shish yoki o'chirishni xohlaysizmi?", reply_markup=markup
    )

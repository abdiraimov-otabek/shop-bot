import logging
from aiogram.types import Message, CallbackQuery
from keyboards.inline.categories import categories_markup, category_cb
from keyboards.inline.products_from_catalog import product_markup, product_cb
from loader import dp, db
from .menu import catalog
from filters import IsUser


@dp.message_handler(IsUser(), text=catalog)
async def process_catalog(message: Message):
    await message.answer("Kategoriyani tanlang:", reply_markup=categories_markup())


@dp.callback_query_handler(IsUser(), text="category")
async def process_category(query: CallbackQuery):
    await query.answer()
    await query.message.answer(
        "Kategoriyani tanlang:", reply_markup=categories_markup()
    )


@dp.callback_query_handler(IsUser(), product_cb.filter(action="add"))
async def add_to_cart_callback(query: CallbackQuery, callback_data: dict):
    db.query(
        """INSERT INTO cart VALUES (%s, %s, 1)""",
        (query.message.chat.id, callback_data["id"]),
    )
    await query.answer("Mahsulot savatga qo'shildi!")


@dp.callback_query_handler(IsUser(), product_cb.filter(action="show"))
async def show_product_callback(query: CallbackQuery, callback_data: dict):
    await query.answer()
    _, title, body, image, price, _ = db.fetchone(
        "SELECT * FROM products WHERE idx = %s", (callback_data["id"],)
    )
    await query.message.answer_photo(
        photo=image,
        caption=f"<b>{title}</b>\n\n{body}\n\nNarxi: {price:,} so'm.",
        reply_markup=product_markup(callback_data["id"], "show"),
    )


@dp.callback_query_handler(IsUser(), category_cb.filter(action="view"))
async def user_catalog_callback(query: CallbackQuery, callback_data: dict):
    await query.answer()
    products = db.fetchall(
        """SELECT * FROM products product 
    WHERE product.tag = (SELECT title FROM categories WHERE idx=%s)
    AND product.idx NOT IN (SELECT idx FROM cart WHERE cid = %s)""",
        (callback_data["id"], query.message.chat.id),
    )
    if len(products) == 0:
        await query.answer("Hech qanday mahsulot yo'q!")
        await query.message.delete()
    else:
        await query.message.answer("Mahsulotni tanlang:")
        [
            await query.message.answer(
                f"<b>{title}</b>\n\n{body}\n\nNarxi: {price:,} so'm.",
                reply_markup=product_markup(idx, "show"),
            )
            for idx, title, body, image, price, tag in products
        ]

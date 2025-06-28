from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loader import db

product_cb = CallbackData("product", "id", "action")


def product_markup(idx="", action="add"):

    global product_cb

    markup = InlineKeyboardMarkup()

    if action == "add":
        markup.add(
            InlineKeyboardButton(
                "Savatga qo'shish",
                callback_data=product_cb.new(id=idx, action="add"),
            )
        )
    elif action == "show":
        markup.add(
            InlineKeyboardButton(
                "Savatga qo'shish",
                callback_data=product_cb.new(id=idx, action="add"),
            )
        )

    return markup

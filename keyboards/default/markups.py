from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

back_message = "👈 Ortga"
confirm_message = "✅ Buyurtmani tasdiqlash"
all_right_message = "✅ Hammasi to'g'ri"
cancel_message = "❌ Bekor qilish"
phone_number = "📞 Telefon raqamni yuborish"


def confirm_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, confirm_message)

    return markup


def back_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)

    return markup


def check_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, all_right_message)

    return markup


def submit_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(cancel_message, all_right_message)

    return markup


def send_contact():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))
    return markup

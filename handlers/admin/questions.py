from handlers.user.menu import admin_questions
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from keyboards.default.markups import all_right_message, cancel_message, submit_markup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.types.chat import ChatActions
from states import AnswerState
from loader import dp, db, bot
from filters import IsAdmin

question_cb = CallbackData("question", "cid", "action")


@dp.message_handler(IsAdmin(), text=admin_questions)
async def process_questions(message: Message):

    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    questions = db.fetchall("SELECT * FROM questions")

    if len(questions) == 0:

        await message.answer("Hech qanday savol yo'q.")

    else:

        await questions_answer(message, questions)


async def questions_answer(message, questions):

    res = ""

    for question in questions:
        res += f"Savol: <b>{question[1]}</b>\n\n"

    await message.answer(res)


@dp.callback_query_handler(IsAdmin(), question_cb.filter(action="answer"))
async def process_answer(query: CallbackQuery, callback_data: dict, state: FSMContext):

    async with state.proxy() as data:
        data["cid"] = callback_data["cid"]

    await query.message.answer("Напиши ответ.", reply_markup=ReplyKeyboardRemove())
    await AnswerState.answer.set()


@dp.message_handler(IsAdmin(), state=AnswerState.answer)
async def process_submit(message: Message, state: FSMContext):

    async with state.proxy() as data:
        data["answer"] = message.text

    await AnswerState.next()
    await message.answer(
        "Убедитесь, что не ошиблись в ответе.", reply_markup=submit_markup()
    )


@dp.message_handler(IsAdmin(), text=cancel_message, state=AnswerState.submit)
async def process_send_answer(message: Message, state: FSMContext):
    await message.answer("Отменено!", reply_markup=ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(IsAdmin(), text=all_right_message, state=AnswerState.submit)
async def process_send_answer(message: Message, state: FSMContext):

    async with state.proxy() as data:

        answer = data["answer"]
        cid = data["cid"]

        question = db.fetchone("SELECT question FROM questions WHERE cid=%s", (cid,))[0]
        db.query("DELETE FROM questions WHERE cid=%s", (cid,))
        text = f"Вопрос: <b>{question}</b>\n\nОтвет: <b>{answer}</b>"

        await message.answer("Отправлено!", reply_markup=ReplyKeyboardRemove())
        await bot.send_message(cid, text)

    await state.finish()

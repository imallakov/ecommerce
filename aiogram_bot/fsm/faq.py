from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from database.requests import get_all_answered_questions, create_new_question
from keyboards.callbackdata import FAQData
from keyboards.inline_keyboards import faq_keyboard, to_main_menu_keyboard

faq_fsm_router = Router()


class FSMqa(StatesGroup):
    ask_question = State()


@faq_fsm_router.callback_query(FAQData.filter(F.event == 'to_faq'))
async def to_answered_questions(query: CallbackQuery, callback_data: FAQData):
    answered_question = await get_all_answered_questions()
    index = callback_data.index
    if len(answered_question) > 0:
        if callback_data.from_menu:
            await query.answer(text='Сначала взгляните пожалуйста на уже отвеченные вопросы, '
                                    'может найдете ответ на свой вопрос😉',
                               show_alert=True)
        question = answered_question[index - 1]
        text = (f'Вопрос:\n{question.question}\n\n'
                f'Ответ админа:\n{question.answer}\n')
        if index >= len(answered_question):
            text += ('\nЕсли не нашли ответ на свой вопрос. Задайте пж его ниже, как только админы ответят '
                     'на ваш вопрос, он появится здесь!')
    else:
        await query.answer()
        text = 'Отвеченных вопросов еще нет! Задайте свой вопрос, как только админы ответят ваш вопрос появится здесь!'
    await query.message.edit_text(text=text, reply_markup=await faq_keyboard(index=index,
                                                                             count_of_questions=len(answered_question)))


@faq_fsm_router.callback_query(FAQData.filter(F.event == 'own_ques'))
async def ask_own_question(query: CallbackQuery, callback_data: FAQData, state: FSMContext):
    await query.answer()
    sent_message = await query.message.edit_text(text='Нам очень жаль что вы не нашли ответ на свой вопрос.\n'
                                                      'Задайте пожалуйста свой вопрос ниже⬇️\n'
                                                      'Мы обязательно ответим на ваш вопрос 😉',
                                                 reply_markup=await to_main_menu_keyboard(text='Отменить'))
    await state.set_state(FSMqa.ask_question)
    await state.update_data(message_id=sent_message.message_id)


@faq_fsm_router.message(StateFilter(FSMqa.ask_question))
async def save_users_question(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data['message_id']
    await message.delete()
    result = await create_new_question(text=message.text)
    if result:
        await message.bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=message_id,
                                            text='Мы сохранили ваш вопрос.\nКак только мы на '
                                                 'него ответим, он появится среди отвеченных вопросов',
                                            reply_markup=await to_main_menu_keyboard(text='Отлично👍🏻'))
    else:
        await message.bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=message_id,
                                            text='Произошла ошибка во время сохранения вашего вопроса!❌\n'
                                                 'Мы уже работаем над ним!🧑🏻‍💻',
                                            reply_markup=await to_main_menu_keyboard(text='Хорошо'))
    await state.clear()
    await state.update_data({})

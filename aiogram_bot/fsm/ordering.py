from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database.requests import get_user, get_all_cartitems_of_user
from keyboards.callbackdata import CartItemData
from keyboards.inline_keyboards import order_keyboard
from utils.save_to_excel import save_order_to_excel_file

order_fsm_router = Router()


class FSMorder(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    enter_address = State()
    enter_contact = State()


@order_fsm_router.callback_query(CartItemData.filter(F.event == 'order'))
async def ask_address(query: CallbackQuery, state: FSMContext):
    cartitems = await get_all_cartitems_of_user(user_id=query.message.chat.id)
    if len(cartitems) == 0:
        await query.answer(
            text='В корзине пусто🤷🏻‍♂️',
            show_alert=True,
        )
    else:
        await state.set_state(FSMorder.enter_address)
        sent_message = await query.message.edit_text(text='Укажите пожалуйста адрес доставки:',
                                                     reply_markup=await order_keyboard(text='Отменить доставку'))
        await state.update_data(message_id=sent_message.message_id)


@order_fsm_router.message(StateFilter(FSMorder.enter_address))
async def address_is_entered(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.delete()
    data = await state.get_data()
    message_id = data['message_id']
    await message.bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=message_id,
                                        text='Адрес сохранён!✅\nУкажите пожалуйста ваш '
                                             'телефон номер, это нужно для того чтоб мы могли подвердить доставку:',
                                        reply_markup=await order_keyboard(text='Отменить доставку'))
    await state.set_state(FSMorder.enter_contact)


@order_fsm_router.message(StateFilter(FSMorder.enter_contact))
async def address_is_entered(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    await message.delete()
    data = await state.get_data()
    message_id = data['message_id']
    await message.bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=message_id,
                                        text='Спасибо!✅\nУже оформляем вашу заявку!',
                                        reply_markup=await order_keyboard(text='Хорошо👍🏻'))
    user = await get_user(user_id=message.chat.id)
    items = await get_all_cartitems_of_user(user_id=user.id)
    await save_order_to_excel_file(user_id=user.id, username=user.username, phone_number=message.text, items=items,
                                   address=data['address'])
    await state.clear()

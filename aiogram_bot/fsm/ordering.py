from tkinter import PhotoImage
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, pre_checkout_query, LabeledPrice
from config_reader import config
from bot import answer_to_pre_checkout_query

from database.requests import get_user, get_all_cartitems_of_user
from keyboards.callbackdata import CartItemData
from keyboards.inline_keyboards import order_keyboard
from utils.save_to_excel import save_order_to_excel_file

order_fsm_router = Router()

payment_token = config.payment_token.get_secret_value()

class FSMorder(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    enter_address = State()
    enter_contact = State()
    payment = State()


@order_fsm_router.callback_query(CartItemData.filter(F.event == 'order'))
async def ask_address(query: CallbackQuery, state: FSMContext):
    cartitems = await get_all_cartitems_of_user(user_id=query.message.chat.id)
    if len(cartitems) == 0:
        await query.answer(
            text='В корзине пусто🤷🏻‍♂️',
            show_alert=True,
        )
    else:
        money = 0
        for item in cartitems:
            money += item.product.price * item.quantity
        await state.set_state(FSMorder.enter_address)
        sent_message = await query.message.edit_text(text='Укажите пожалуйста адрес доставки:',
                                                     reply_markup=await order_keyboard(text='Отменить доставку'))
        await state.update_data(message_id=sent_message.message_id)
        await state.update_data(money=money)


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
async def contact_is_entered(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    await message.delete()
    data = await state.get_data()
    money = data['money']
    message_id = data['message_id']
    phone = message.text
    address = data['address']
    await message.bot.edit_message_text(chat_id=message.chat.id, message_id=message_id,
                                        text=f'Произведите пожалуйста оплату за товары снизу⬇️')
    sent_invoice = await message.bot.send_invoice(
        chat_id=message.chat.id,
        title='Доставка товаров в корзине',
        description=f'Оплата заказываемых товаров',
        payload=f'user:{message.chat.id}',
        provider_token=payment_token,
        currency='RUB',
        prices=[
            LabeledPrice(
                label='Суммарная стоимость товаров',
                amount=100 * 100, # in release version replase one of the "100" with "money" variable
            ),
        ],
        start_parameter='djangoshopbot',
        provider_data=None,
        protect_content=True,
    )
    await state.update_data(sent_invoice=sent_invoice.message_id)
    await state.update_data(phone=phone)
    await state.update_data(address=address)
    await state.set_state(FSMorder.payment)


@order_fsm_router.pre_checkout_query()
async def pre_checkout_query_answer(pcq: pre_checkout_query):
    await answer_to_pre_checkout_query(pcq.id, answer=True, error='')
        

@order_fsm_router.message(F.successful_payment)
async def successfull_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.chat.id
    phone = data['phone']
    address = data['address']
    message_id = data['message_id']
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    error: bool = False
    user = await get_user(user_id=user_id)
    if user is not None:
        items = await get_all_cartitems_of_user(user_id=user.id)
        if len(items)>0:
            result = await save_order_to_excel_file(user_id=user.id, username=user.username, phone_number=phone, items=items,
                                        address=address)
            if not result:
                error = True
        else:
            error=True
    else:
        error=True
    if not error:
        await message.answer(text='Спасибо!✅\nУже оформляем вашу заявку!',
                             reply_markup=await order_keyboard(text='Хорошо👍🏻'))
    else:
        await message.answer(text=('Произошла ошибка!\nПопробуйте перезапустить бота и заново заказать доставку'
                                   '\nЕсли ошибка повторится дайте нам знать пожалуйста в разделе FAQ'),
                             reply_markup=await order_keyboard(text='Хорошо'))
    await state.update_data({})
    await state.clear()

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from database.requests import get_product_by_id, add_product_to_cart
from keyboards.inline_keyboards import asking_to_add_product_to_cart

shopping_fsm_router = Router()


class FSMshop(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    enter_quantity = State()
    fact_checking = State()


@shopping_fsm_router.callback_query(F.data == 'cancel_adding_item_to_cart', StateFilter(FSMshop.enter_quantity))
@shopping_fsm_router.callback_query(F.data == 'dont_add_item_to_cart', StateFilter(FSMshop.fact_checking))
async def cancel_adding_of_item_to_cart(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.update_data({})
    await state.clear()
    await query.answer(text='Покупка отменена, можете продолжить просмотр товаров🛍️', show_alert=True)


@shopping_fsm_router.message(StateFilter(FSMshop.enter_quantity))
async def fsm_enter_product_quantity(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data['message_id']
    await message.delete()
    if not message.text.isdigit():
        await message.bot.edit_message_text(
            text='Напишите пожалуйста цифрами количество товара которую хотите добавить в корзину:',
            chat_id=message.chat.id, message_id=message_id)
    else:
        quantity = int(message.text)
        if quantity > 0:
            product_id = data['product_id']
            product = await get_product_by_id(product_id=product_id)
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id,
                text=f'Название товара: {product.name}\n'
                     f'Цена: {product.price}\n'
                     f'Количество: {quantity}\n\n'
                     f'Добавить в корзину?🛒',
                reply_markup=await asking_to_add_product_to_cart()
            )
            await state.set_state(FSMshop.fact_checking)
            await state.update_data(quantity=quantity)
        else:
            await message.bot.edit_message_text(
                text='Неправильный формат ввода!\n'
                     'Напишите пожалуйста цифрами количество товара которую хотите добавить в корзину:',
                chat_id=message.chat.id, message_id=message_id)


@shopping_fsm_router.callback_query(F.data == 'add_item_to_cart', StateFilter(FSMshop.fact_checking))
async def cancel_adding_of_item_to_cart(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    quantity = data['quantity']
    user_id = query.message.chat.id
    result = await add_product_to_cart(user_id=user_id, product_id=product_id, quantity=quantity)
    await query.message.delete()
    await state.update_data({})
    await state.clear()
    if result:
        await query.answer(text='✅Товар успешно добавлен в корзину🛒', show_alert=True)
    else:
        await query.answer(text='❌Произошла ошибка! Разработчики уже уведомлены!', show_alert=True)

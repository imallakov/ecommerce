from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from database.requests import get_all_cartitems_of_user, delete_item_from_cart
from keyboards.callbackdata import CartItemData
from keyboards.inline_keyboards import my_cart_menu_keyboard, cartitem_keyboard, are_you_sure_to_delete_keyboard

cart_router = Router()


@cart_router.callback_query(CartItemData.filter(F.event == 'to_my_cart'))
async def to_my_cart_menu(query: CallbackQuery, callback_data: CartItemData, state: FSMContext):
    if state is not None:
        if not await state.get_state() is None:
            await state.update_data({})
            await state.clear()
    if callback_data.from_menu:
        await query.message.edit_text(
            text='Ваша корзина🛒',
            reply_markup=await my_cart_menu_keyboard()
        )
    else:
        await query.message.delete()
        await query.message.answer(
            text='Ваша корзина🛒',
            reply_markup=await my_cart_menu_keyboard()
        )
    await query.answer()


@cart_router.callback_query(CartItemData.filter(F.event == 'to_items'))
async def list_of_users_items(query: CallbackQuery, callback_data: CartItemData):
    cartitems = await get_all_cartitems_of_user(user_id=query.message.chat.id)
    if len(cartitems) == 0:
        await query.answer(
            text='В корзине пусто🤷🏻‍♂️',
            show_alert=True,
        )
    else:
        await query.answer()
        index = callback_data.index - 1
        if index < 0:
            index = 0
        elif index >= len(cartitems):
            index = len(cartitems) - 1
        await query.message.delete()
        product = cartitems[index].product
        quantity = cartitems[index].quantity
        await query.bot.send_photo(
            chat_id=query.message.chat.id,
            photo=FSInputFile(path='photos/'+product.photo),
            caption=f'{product.name}\n\nPrice: {product.price}\n'
                    f'Quantity: {quantity}'
                    f'\n\nDescription:\n{product.description}',
            reply_markup=await cartitem_keyboard(index=index + 1, count_of_items=len(cartitems), product_id=product.id)
        )


@cart_router.callback_query(CartItemData.filter(F.event == 'delete'))
async def deleting_item_from_cart(query: CallbackQuery, callback_data: CartItemData):
    caption = query.message.caption
    await query.message.edit_caption(caption=caption + '\n\nУверены что хотите удалить товар из корзины?',
                                     reply_markup=await are_you_sure_to_delete_keyboard(index=callback_data.index,
                                                                                        product_id=callback_data.product_id))
    await query.answer()


@cart_router.callback_query(CartItemData.filter(F.event == 'do_del'))
async def sure_delete_item_from_cart(query: CallbackQuery, callback_data: CartItemData):
    product_id = callback_data.product_id
    result = await delete_item_from_cart(user_id=query.message.chat.id, product_id=product_id)
    if result:
        await query.answer(caption='✅Товар успешно удалён из корзины🗑️', show_alert=True)
        cartitems = await get_all_cartitems_of_user(user_id=query.message.chat.id)
        if len(cartitems) == 0:
            await query.message.delete()
            await query.message.answer(
                text='Ваша корзина🛒',
                reply_markup=await my_cart_menu_keyboard()
            )
        else:
            await query.answer()
            index = callback_data.index - 1
            if index < 0:
                index = 0
            elif index >= len(cartitems):
                index = len(cartitems) - 1
            await query.message.delete()
            product = cartitems[index].product
            quantity = cartitems[index].quantity
            await query.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=FSInputFile(path=product.photo),
                caption=f'{product.name}\n\nPrice: {product.price}\n'
                        f'Quantity: {quantity}'
                        f'\n\nDescription:\n{product.description}',
                reply_markup=await cartitem_keyboard(index=index + 1, count_of_items=len(cartitems),
                                                     product_id=product.id))
    else:
        await query.answer(text='❌Произошла ошибка! Уже работаем над исправлением!', show_alert=True)

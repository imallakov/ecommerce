from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from database.requests import get_all_categories, get_subcategories_of_category, get_products_of_subcategory
from fsm.product_quantity import FSMshop
from keyboards.callbackdata import CategoryData, SubCatData, ProductData
from keyboards.inline_keyboards import categories_keyboard, subcategories_keyboard, product_keyboard, \
    cancel_adding_item_to_cart

shopping_router = Router()


@shopping_router.callback_query(CategoryData.filter(F.event == 'to_categories'))
async def checking_subscription(query: CallbackQuery, callback_data: CategoryData):
    categories = await get_all_categories()
    if len(categories) > 0:
        await query.message.edit_text(text="Категории товаров:",
                                      reply_markup=await categories_keyboard(index=callback_data.index))
        await query.answer()
    else:
        await query.answer(text='Каталог пуст🤷🏻‍♂️', show_alert=True)


@shopping_router.callback_query(SubCatData.filter(F.event == 'to_subcategories'))
async def checking_subscription(query: CallbackQuery, callback_data: SubCatData):
    subcategories = await get_subcategories_of_category(category_id=callback_data.cat_id)
    if len(subcategories) > 0:
        if callback_data.index == -1:
            await query.message.delete()
            await query.message.answer(text="Выберите подкатегорию:",
                                       reply_markup=await subcategories_keyboard(category_id=callback_data.cat_id,
                                                                                 index=1))
        else:
            await query.message.edit_text(text="Выберите подкатегорию:",
                                          reply_markup=await subcategories_keyboard(category_id=callback_data.cat_id,
                                                                                    index=callback_data.index))
        await query.answer()
    else:
        await query.answer(text='Пусто🤷🏻‍♂️', show_alert=True)


@shopping_router.callback_query(ProductData.filter(F.event == 'prod'))
async def checking_subscription(query: CallbackQuery, callback_data: ProductData):
    products = await get_products_of_subcategory(subcategory_id=callback_data.subcat_id)
    if len(products) > 0:
        product = products[callback_data.index - 1]
        await query.message.delete()
        await query.bot.send_photo(chat_id=query.message.chat.id, photo=FSInputFile(path='photos/'+product.photo),
                                   caption=f'{product.name}\n\nPrice: {product.price}'
                                           f'\n\nDescription:\n{product.description}',
                                   reply_markup=await product_keyboard(cat_id=product.subcategory.category_id,
                                                                       subcat_id=product.subcategory_id,
                                                                       index=callback_data.index,
                                                                       count_of_products=len(products),
                                                                       product_id=product.id))
        await query.answer()
    else:
        await query.answer(text='Пусто🤷🏻‍♂️', show_alert=True)


@shopping_router.callback_query(ProductData.filter(F.event == 'add_to_cart'))
async def adding_product_to_cart(query: CallbackQuery, callback_data: ProductData, state: FSMContext):
    await query.answer()
    sent_message = await query.message.answer(
        text='Укажите, пожалуйста цифрами,  какое количество вы хотели бы приобрести?',
        reply_markup=await cancel_adding_item_to_cart())
    product_id = callback_data.index
    await state.set_state(FSMshop.enter_quantity)
    await state.update_data(message_id=sent_message.message_id)
    await state.update_data(product_id=product_id)

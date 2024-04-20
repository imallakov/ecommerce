from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.requests import get_all_categories, get_subcategories_of_category, get_all_subscription_chats
from keyboards.callbackdata import CategoryData, SubCatData, ProductData, CartItemData, FAQData


async def subscription_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    chats = await get_all_subscription_chats()
    for chat in chats:
        kb.add(
            InlineKeyboardButton(
                text=chat.name,
                url=f"t.me/{chat.username}"
            ),
        )
    kb.add(
        InlineKeyboardButton(
            text='Проверить✅',
            callback_data='check_subscriptions',
        )
    )
    kb.adjust(1, repeat=True)
    return kb.as_markup()


async def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(
            text='Категории',
            callback_data=CategoryData(event='to_categories', index=1).pack()
        ),
        InlineKeyboardButton(
            text='Корзина',
            callback_data=CartItemData(event='to_my_cart', index=-1, product_id=0, from_menu=True).pack()
        ),
        InlineKeyboardButton(
            text='FAQ',
            callback_data=FAQData(event='to_faq', index=1, from_menu=True).pack()
        ),
    )
    kb.adjust(1, repeat=True)
    return kb.as_markup()


async def categories_keyboard(index) -> InlineKeyboardMarkup:
    categories = await get_all_categories()
    kb = InlineKeyboardBuilder()
    for cat in categories[((index - 1) * 5):(index * 5)]:
        kb.add(
            InlineKeyboardButton(
                text=cat.name,
                callback_data=SubCatData(event='to_subcategories', cat_id=cat.id, index=1).pack()
            ),
        )
    navbar = InlineKeyboardBuilder()
    count = len(categories) // 5
    count += 1 if len(categories) % 5 > 0 else 0
    navbar.add(
        InlineKeyboardButton(
            text='⬅️',
            callback_data=CategoryData(event='to_categories', index=index - 1).pack() if index > 1 else "ignore"
        ),
        InlineKeyboardButton(
            text=f'{index}/{count}',
            callback_data="ignore"
        ),
        InlineKeyboardButton(
            text='➡️',
            callback_data=CategoryData(event='to_categories', index=index + 1).pack() if index < count else "ignore"
        ),
    )
    navbar.add(
        InlineKeyboardButton(
            text='Назад',
            callback_data="main_menu",
        )
    )
    kb.adjust(1, repeat=True)
    navbar.adjust(3, 1)
    kb.attach(navbar)
    return kb.as_markup()


async def subcategories_keyboard(category_id, index) -> InlineKeyboardMarkup:
    subcategories = await get_subcategories_of_category(category_id=category_id)
    kb = InlineKeyboardBuilder()
    for subcat in subcategories[(index - 1) * 5:index * 5]:
        kb.add(
            InlineKeyboardButton(
                text=subcat.name,
                callback_data=ProductData(event='prod', subcat_id=subcat.id, index=1, from_subcat=True).pack()
            ),
        )
    navbar = InlineKeyboardBuilder()
    count = len(subcategories) // 5
    count += 1 if len(subcategories) % 5 > 0 else 0

    navbar.add(
        InlineKeyboardButton(
            text='⬅️',
            callback_data=SubCatData(event='to_subcategories', cat_id=category_id,
                                     index=index - 1).pack() if index > 1 else "ignore"
        ),
        InlineKeyboardButton(
            text=f'{index}/{count}',
            callback_data="ignore"
        ),
        InlineKeyboardButton(
            text='➡️',
            callback_data=CategoryData(event='to_subcategories', cat_id=category_id,
                                       index=index + 1).pack() if index < count else "ignore"
        ),
    )
    navbar.add(
        InlineKeyboardButton(
            text='Назад',
            callback_data=CategoryData(event="to_categories", index=1).pack(),
        )
    )
    kb.adjust(1, repeat=True)
    navbar.adjust(3, 1)
    kb.attach(navbar)
    return kb.as_markup()


async def product_keyboard(cat_id, subcat_id, index, count_of_products, product_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(
            text='Add to Cart🛒',
            callback_data=ProductData(event="add_to_cart", subcat_id=0, index=product_id, from_subcat=False).pack()
        )
    )
    navbar = InlineKeyboardBuilder()
    navbar.add(
        InlineKeyboardButton(
            text='⬅️',
            callback_data=ProductData(event='prod', subcat_id=subcat_id, index=index - 1,
                                      from_subcat=False).pack() if index > 1 else "ignore"
        ),
        InlineKeyboardButton(
            text=f'{index}/{count_of_products}',
            callback_data="ignore"
        ),
        InlineKeyboardButton(
            text='➡️',
            callback_data=ProductData(event='prod', subcat_id=subcat_id, index=index + 1,
                                      from_subcat=False).pack() if index < count_of_products else "ignore"
        ),
    )
    navbar.add(
        InlineKeyboardButton(
            text='Назад',
            callback_data=SubCatData(event='to_subcategories', cat_id=cat_id, index=-1).pack(),
        )
    )
    kb.adjust(1, repeat=True)
    navbar.adjust(3, 1)
    kb.attach(navbar)
    return kb.as_markup()


async def cancel_adding_item_to_cart() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(
            text='Отменить покупку',
            callback_data="cancel_adding_item_to_cart",
        )
    )
    return kb.as_markup()


async def asking_to_add_product_to_cart() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(
            text='Нет',
            callback_data="dont_add_item_to_cart",
        ),
        InlineKeyboardButton(
            text='Да🛒',
            callback_data="add_item_to_cart",
        ),
    )
    kb.adjust(2)
    return kb.as_markup()


async def my_cart_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(
            text='Просмотр товаров',
            callback_data=CartItemData(event='to_items', index=1, product_id=0, from_menu=True).pack()
        ),
        InlineKeyboardButton(
            text='Заказать доставку',
            callback_data=CartItemData(event='order', index=0, product_id=0, from_menu=True).pack()
        ),
        InlineKeyboardButton(
            text='Назад',
            callback_data="main_menu",
        )
    )
    kb.adjust(1, repeat=True)
    return kb.as_markup()


async def cartitem_keyboard(index, count_of_items, product_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(
            text='Удалить из корзины🗑️',
            callback_data=CartItemData(event='delete', index=index, product_id=product_id, from_menu=False).pack()
        )
    )
    navbar = InlineKeyboardBuilder()
    navbar.add(
        InlineKeyboardButton(
            text='⬅️',
            callback_data=CartItemData(event='to_items', index=index - 1, product_id=product_id,
                                       from_menu=False).pack() if index > 1 else 'ignore',
        ),
        InlineKeyboardButton(
            text=f'{index}/{count_of_items}',
            callback_data='ignore',
        ),
        InlineKeyboardButton(
            text='➡️',
            callback_data=CartItemData(event='to_items', index=index + 1, product_id=product_id,
                                       from_menu=False).pack() if index < count_of_items else 'ignore',
        ),
        InlineKeyboardButton(
            text='Назад в корзину',
            callback_data=CartItemData(event='to_my_cart', index=-1, product_id=0, from_menu=False).pack()
        )
    )
    navbar.adjust(3, 1)
    kb.adjust(1, repeat=True)
    kb.attach(navbar)
    return kb.as_markup()


async def are_you_sure_to_delete_keyboard(index, product_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(
            text='Нет',
            callback_data=CartItemData(event="to_items", index=index, product_id=product_id, from_menu=False).pack()
        ),
        InlineKeyboardButton(
            text='Да🗑️',
            callback_data=CartItemData(event="do_del", index=index, product_id=product_id, from_menu=False).pack()
        )
    )
    kb.adjust(2)
    return kb.as_markup()


async def order_keyboard(text) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(
            text=text,
            callback_data=CartItemData(event='to_my_cart', index=0, product_id=0, from_menu=True).pack(),
        )
    )
    return kb.as_markup()


async def faq_keyboard(index, count_of_questions) -> InlineKeyboardMarkup:
    navbar = InlineKeyboardBuilder()
    if index >= count_of_questions:
        navbar.add(
            InlineKeyboardButton(
                text='Задать свой вопрос🗨️',
                callback_data=FAQData(event='own_ques', index=0, from_menu=False).pack()
            )
        )
    navbar.add(
        InlineKeyboardButton(
            text='⬅️',
            callback_data=FAQData(event='to_faq', index=index - 1, from_menu=False).pack() if index > 1 else "ignore"
        ),
        # InlineKeyboardButton(
        #     text=f'{index}/{count_of_questions}',
        #     callback_data="ignore"
        # ),
        InlineKeyboardButton(
            text='➡️',
            callback_data=FAQData(event='to_faq', index=index + 1,
                                  from_menu=False).pack() if index < count_of_questions else "ignore"
        ),
    )
    navbar.add(
        InlineKeyboardButton(
            text='Назад',
            callback_data="main_menu",
        )
    )
    if index >= count_of_questions:
        navbar.adjust(1, 2, 1)
    else:
        navbar.adjust(2, 1)
    return navbar.as_markup()


async def to_main_menu_keyboard(text) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(
        InlineKeyboardButton(
            text=text,
            callback_data="main_menu",
        )
    )
    return kb.as_markup()

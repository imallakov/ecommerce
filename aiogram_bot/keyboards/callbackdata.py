from aiogram.filters.callback_data import CallbackData


class CategoryData(CallbackData, prefix='category'):
    event: str
    index: int


class SubCatData(CallbackData, prefix='subcategory'):
    event: str
    cat_id: int
    index: int


class ProductData(CallbackData, prefix='product'):
    event: str
    subcat_id: int
    index: int
    from_subcat: bool


class CartItemData(CallbackData, prefix='cartitem'):
    event: str
    index: int
    product_id: int
    from_menu: bool


class FAQData(CallbackData, prefix='faq'):
    event: str
    index: int
    from_menu: bool

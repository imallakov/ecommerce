from types import NoneType
from sqlalchemy import select, exc
from sqlalchemy.orm import selectinload

# from bot import bot_send_message, bot_send_error_message
from .models import User, Chat, async_session, Product, Category, Subcategory, CartItem, QuestionAnswer


async def is_user_exists(user_id: int) -> bool:
    try:
        async with async_session() as session:
            sql_res = await session.execute(select(User).where(User.id == user_id))
            res = sql_res.scalars().first()
            if type(res) is not NoneType:
                return True
            else:
                return False
    except exc.SQLAlchemyError as error:
        # await bot_send_error_message(
        #     f'is_user_exists:\nuser_id={user_id}\nError: {error.__str__()}')
        return False


async def create_user(user_id: int, username: str | None) -> User | None:
    try:
        if type(username) is None:
            username = ''
        if not await is_user_exists(user_id):
            async with async_session() as session:
                user = User(id=user_id, username=username)
                session.add(user)
                await session.commit()
                return await get_user(user_id)
        else:
            async with async_session() as session:
                result = await session.execute(
                    select(User)
                    .filter(User.id == user_id)  # type: ignore
                )
                user = result.scalars().first()
                user.username = username
                await session.commit()
                return await get_user(user_id)
    except exc.SQLAlchemyError as error:
        # await bot_send_error_message(
        #     f'create_user:\nuser_id={user_id}\nusername={username}\nError: {error.__str__()}')
        return None


async def get_user(user_id: int) -> User | None:
    try:
        async with async_session() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.cart_items))
                .filter(User.id == user_id)  # type: ignore
            )
            return result.scalars().first()
    except exc.SQLAlchemyError as error:
        # await bot_send_error_message(
        #     f'get_user:\nuser_id={user_id}\nError: {error.__str__()}')
        return None


async def add_product_to_cart(user_id: int, product_id: int, quantity: int) -> bool:
    try:
        async with async_session() as session:
            result = await session.execute(
                select(CartItem)
                .filter(CartItem.product_id == product_id, CartItem.user_id == user_id)  # type: ignore
            )
            cartitem = result.scalars().first()
            if cartitem is None:
                cartitem = CartItem(product_id=product_id, quantity=quantity, user_id=user_id)
            else:
                cartitem.quantity += quantity
            session.add(cartitem)
            await session.commit()
        return True
    except exc.SQLAlchemyError as error:
        # await bot_send_error_message(
        #     f'create_user:\nuser_id={user_id}\nusername={username}\nError: {error.__str__()}')
        return False


async def get_all_subscription_chats() -> list[Chat]:
    try:
        async with async_session() as session:
            chats = await session.execute(select(Chat))
            return chats.scalars().all()
    except exc.SQLAlchemyError as error:
        # await bot_send_error_message(
        #     f'get_all_chats:\nError: {error.__str__()}')
        print('error', error)
        return []


async def get_all_categories() -> list[Category]:
    try:
        async with async_session() as session:
            caregories = await session.execute(select(Category).order_by(Category.id))
            return caregories.scalars().all()
    except exc.SQLAlchemyError as error:
        print('error', error)
        # await bot_send_error_message(
        #     f'get_all_chats:\nError: {error.__str__()}')
        return []


async def get_subcategories_of_category(category_id) -> list[Subcategory]:
    try:
        async with async_session() as session:
            subcaregories = await session.execute(
                select(Subcategory).where(Subcategory.category_id == category_id).order_by(Subcategory.id))
            return subcaregories.scalars().all()
    except exc.SQLAlchemyError as error:
        print('error', error)
        # await bot_send_error_message(
        #     f'get_all_chats:\nError: {error.__str__()}')
        return []


async def get_products_of_subcategory(subcategory_id) -> list[Product]:
    try:
        async with async_session() as session:
            products = await session.execute(
                select(Product)
                .where(Product.subcategory_id == subcategory_id)
                .order_by(Product.id)
                .options(selectinload(Product.subcategory))
            )
            return products.scalars().all()
    except exc.SQLAlchemyError as error:
        print('error', error)
        # await bot_send_error_message(
        #     f'get_all_chats:\nError: {error.__str__()}')
        return []


async def get_product_by_id(product_id) -> Product | None:
    try:
        async with async_session() as session:
            product = await session.execute(
                select(Product)
                .where(Product.id == product_id)
            )
            return product.scalars().first()
    except exc.SQLAlchemyError as error:
        print('error', error)
        return None


async def get_all_cartitems_of_user(user_id) -> list[CartItem]:
    try:
        async with async_session() as session:
            cartitems = await session.execute(
                select(CartItem)
                .where(CartItem.user_id == user_id)
                .options(selectinload(CartItem.product))
            )
            return cartitems.scalars().all()
    except exc.SQLAlchemyError as error:
        print('error', error)
        return []


async def clear_all_cartitems_of_user(user_id):
    try:
        async with async_session() as session:
            cart_items = await session.execute(
                select(CartItem)
                .where(CartItem.user_id == user_id)
            )
            cart_items = cart_items.scalars().all()
            if cart_items:
                for item in cart_items:
                    await session.delete(item)
                await session.commit()
    except exc.SQLAlchemyError as error:
        print('error', error)


async def delete_item_from_cart(user_id, product_id) -> bool:
    try:
        async with async_session() as session:
            cart_item = await session.execute(
                select(CartItem)
                .where(CartItem.user_id == user_id, CartItem.product_id == product_id)
                .limit(1)
            )
            cart_item = cart_item.scalars().first()
            if cart_item:
                await session.delete(cart_item)
                await session.commit()
                return True
            return False
    except exc.SQLAlchemyError as error:
        print('error', error)
        return False


async def get_all_answered_questions() -> list[QuestionAnswer]:
    try:
        async with async_session() as session:
            qas = await session.execute(
                select(QuestionAnswer)
                .where(QuestionAnswer.answer.isnot(None))
                .order_by(QuestionAnswer.id)
            )
            return qas.scalars().all()
    except exc.SQLAlchemyError as error:
        print('error', error)
        return []


async def create_new_question(text) -> bool:
    try:
        async with async_session() as session:
            ques = QuestionAnswer(question=text, answer=None)
            session.add(ques)
            await session.commit()
        return True
    except exc.SQLAlchemyError as error:
        print('error', error)
        # await bot_send_error_message(
        #     f'create_user:\nuser_id={user_id}\nusername={username}\nError: {error.__str__()}')
    return False

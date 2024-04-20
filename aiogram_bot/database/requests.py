from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist  # Import ObjectDoesNotExist
from bot import bot_send_error_message
from .models import User, Chat, Product, Category, Subcategory, CartItem, QuestionAnswer, Mailing


async def is_user_exists(user_id: int) -> bool:
    try:
        await User.objects.get(id=user_id)  # Use get for async fetching
        return True
    except User.DoesNotExist:
        return False
    except Exception as error:
        await bot_send_error_message(f'is_user_exists:\nuser_id={user_id}\nError: {error}')


async def create_user(user_id: int, username: str | None) -> User | None:
    try:
        user, created = await sync_to_async(User.objects.get_or_create)(id=user_id, defaults={
            "username": username})  # Use get_or_create
        return user
    except Exception as error:
        await bot_send_error_message(f'create_user:\nuser_id={user_id}\nusername={username}\nError: {error}')
        return None  # Return None on error


async def get_user(user_id: int) -> User | None:
    try:
        user = await User.objects.prefetch_related(  # Use prefetch_related
            'cart_items__product'
        ).aget(id=user_id)
        return user
    except User.DoesNotExist:
        return None
    except Exception as error:
        await bot_send_error_message(f'get_user:\nuser_id={user_id}\nError: {error}')


async def get_all_users() -> list[User]:
    try:
        users = await sync_to_async(list)(
            User.objects.all().order_by('id'))  # Execute synchronously and convert to list
        return users
    except Exception as error:
        await bot_send_error_message(f'get_all_users:\nError: {error}')
        return []


async def get_user_subscription_status(user_id) -> bool:
    try:
        user = await sync_to_async(User.objects.get)(id=user_id)  # Use sync_to_async to execute synchronously
        return user.is_subscription_complete
    except User.DoesNotExist:
        return False
    except Exception as error:
        await bot_send_error_message(f'get_user_subscription_status:\nuser_id={user_id}\nError: {error}')
        return False


async def change_user_subscription_status(user_id, status: bool) -> bool:
    try:
        user = await sync_to_async(User.objects.get)(id=user_id)
        user.is_subscription_complete = status
        await sync_to_async(user.save)()  # Save the user synchronously
        return True
    except Exception as error:
        await bot_send_error_message(
            f'change_user_subscription_status:\nuser_id={user_id}\nstatus={status}\nError: {error}')
        return False


async def add_product_to_cart(user_id: int, product_id: int, quantity: int) -> bool:
    try:
        cartitem, created = await CartItem.objects.aget_or_create(
            user_id=user_id, product_id=product_id,
            defaults={"quantity": quantity}
        )
        if not created:
            cartitem.quantity += quantity
            await cartitem.asave()
        return True
    except Exception as error:
        await bot_send_error_message(
            f'add_product_to_cart:\nuser_id={user_id}\nproduct_id={product_id}\nError: {error}')


async def get_all_subscription_chats() -> list[Chat]:
    try:
        chats = await sync_to_async(list)(
            Chat.objects.all().order_by('id'))  # Execute synchronously and convert to list
        return chats
    except Exception as error:
        await bot_send_error_message(f'get_all_subscription_chats:\nError: {error}')
        return []  # Return an empty list on error


# ... (previous functions)

async def get_all_categories() -> list[Category]:
    try:
        categories = await sync_to_async(list)(
            Category.objects.all().order_by('id'))  # Execute synchronously and convert to list
        return categories
    except Exception as error:
        await bot_send_error_message(f'get_all_categories:\nError: {error}')
        return []


async def get_subcategories_of_category(category_id) -> list[Subcategory]:
    try:
        return await sync_to_async(list)(Subcategory.objects.filter(category_id=category_id).order_by('id'))
    except Exception as error:
        await bot_send_error_message(f'get_subcategories_of_category:\ncategory_id={category_id}\nError: {error}')
        return []


async def get_products_of_subcategory(subcategory_id) -> list[Product]:
    try:
        return await sync_to_async(list)(
            Product.objects.select_related('subcategory').filter(subcategory_id=subcategory_id).order_by('id'))
    except Exception as error:
        await bot_send_error_message(f'get_products_of_subcategory:\nsubcategory_id={subcategory_id}\nError: {error}')
        return []


async def get_product_by_id(product_id) -> Product | None:
    try:
        return await Product.objects.aget(id=product_id)
    except Product.DoesNotExist:
        return None
    except Exception as error:
        await bot_send_error_message(f'get_product_by_id:\nproduct_id={product_id}\nError: {error}')


async def get_all_cartitems_of_user(user_id) -> list[CartItem]:
    try:
        cart_items = await sync_to_async(list)(
            CartItem.objects.select_related('product').filter(user_id=user_id).order_by(
                'id'))  # Execute synchronously and convert to list
        return cart_items
    except Exception as error:
        await bot_send_error_message(f'get_all_cartitems_of_user:\nuser_id={user_id}\nError: {error}')
        return []


async def clear_all_cartitems_of_user(user_id) -> bool:
    try:
        await CartItem.objects.filter(user_id=user_id).adelete()
        return True
    except Exception as error:
        await bot_send_error_message(f'clear_all_cartitems_of_user:\nuser_id={user_id}\nError: {error}')


async def delete_item_from_cart(user_id, product_id) -> bool:
    try:
        await CartItem.objects.filter(user_id=user_id, product_id=product_id).adelete()
        return True
    except Exception as error:
        await bot_send_error_message(
            f'delete_item_from_cart:\nuser_id={user_id}\nproduct_id={product_id}\nError: {error}')


async def get_all_answered_questions() -> list[QuestionAnswer]:
    try:
        answered_questions = await sync_to_async(list)(QuestionAnswer.objects.filter(answer__isnull=False).order_by(
            'id'))  # Execute synchronously and convert to list
        return answered_questions
    except Exception as error:
        await bot_send_error_message(f'get_all_answered_questions:\nError: {error}')
        return []


async def create_new_question(text) -> bool:
    try:
        await sync_to_async(QuestionAnswer.objects.create)(question=text,
                                                           answer=None)  # Use sync_to_async for creating objects
        return True
    except Exception as error:
        await bot_send_error_message(f'create_new_question:\ntext={text}\nError: {error}')
        return False  # Return False on error


async def get_mailing_by_id(mailing_id) -> Mailing | None:
    try:
        return await Mailing.objects.aget(id=mailing_id)
    except Mailing.DoesNotExist:
        return None
    except Exception as error:
        await bot_send_error_message(f'get_mailing_by_id:\nmailing_id={mailing_id}\nError: {error}')

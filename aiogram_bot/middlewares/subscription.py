from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

from database.requests import get_user_subscription_status
from keyboards.inline_keyboards import subscription_keyboard


class SubscriptionCallbackMiddleware(BaseMiddleware):
    async def subscription_status(self, user_id) -> bool:
        return await get_user_subscription_status(user_id=user_id)

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        # Можно подстраховаться и игнорировать мидлварь,
        # если она установлена по ошибке НЕ на колбэки
        if not isinstance(event, CallbackQuery) or event.data == 'check_subscriptions':
            # тут как-нибудь залогировать
            return await handler(event, data)

        if await self.subscription_status(event.message.chat.id):
            return await handler(event, data)

        if event.message.photo is not None:
            await event.message.delete()
            await event.message.answer(
                text="Подпишитесь пожалуйста на наши каналы и чаты чтоб продолжить использование бота",
                reply_markup=await subscription_keyboard())
        else:
            await event.message.edit_text(
                text="Подпишитесь пожалуйста на наши каналы и чаты чтоб продолжить использование бота",
                reply_markup=await subscription_keyboard())
        return

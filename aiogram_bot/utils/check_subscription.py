from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from database.models import Chat
from database.requests import get_all_subscription_chats


async def check_subscription(bot: Bot, user_id) -> list[Chat]:
    chats = await get_all_subscription_chats()
    for chat in chats:
        if (await bot.get_chat_member(chat_id=chat.id, user_id=user_id)).status == ChatMemberStatus.LEFT:
            return chats
    return []
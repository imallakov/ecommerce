import asyncio

from config_reader import config
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramRetryAfter

bot = Bot(token=config.bot_token.get_secret_value())


async def answer_to_pre_checkout_query(pcq_id, answer, error):
    if answer:
        await bot.answer_pre_checkout_query(pre_checkout_query_id=pcq_id, ok=answer)
    else:
        await bot.answer_pre_checkout_query(pre_checkout_query_id=pcq_id, ok=answer, error_message=error)


async def bot_send_error_message(text: str):
    try:
        return await bot.send_message(chat_id=config.errors_chat_id.get_secret_value(), text=text)
    except Exception as error:
        print(f'error sending error message: {text}   to chat, sending error: ', error.__str__())


async def bot_send_photo(user_id, photo_url, message):
    try:
        await bot.send_photo(
            chat_id=user_id,
            photo=FSInputFile(path='photos/' + photo_url),
            caption=message,
        )
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await bot_send_photo(user_id=user_id, photo_url=photo_url, message=message)
    except Exception as e:
        pass


async def bot_send_message(user_id, message):
    try:
        await bot.send_message(
            chat_id=user_id,
            text=message,
        )
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        await bot_send_message(user_id=user_id, message=message)
    except Exception as e:
        pass


async def bot_send_mailings(mailing_id):
    from database.requests import get_mailing_by_id, get_all_users
    mail = await get_mailing_by_id(mailing_id=mailing_id)
    users = await get_all_users()

    for user in users:
        if mail.photo and mail.photo.file:  # Check if photo attribute has a file associated with it
            await bot_send_photo(user_id=user.id, photo_url=mail.photo.url, message=mail.message)
        else:
            await bot_send_message(user_id=user.id, message=mail.message)
        await asyncio.sleep(.05)

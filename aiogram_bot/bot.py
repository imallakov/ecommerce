from config_reader import config
from aiogram import Bot

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

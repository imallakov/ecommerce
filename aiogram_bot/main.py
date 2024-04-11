from aiogram import Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.types import BotCommand, BotCommandScopeDefault
import asyncio
import logging

from bot import bot
from config_reader import config
from fsm.faq import faq_fsm_router
from fsm.ordering import order_fsm_router
from fsm.product_quantity import shopping_fsm_router
from handlers.cart import cart_router
from handlers.shopping import shopping_router
from handlers.start import start_command_router

dp = Dispatcher()

dp.include_router(start_command_router)
dp.include_router(shopping_router)
dp.include_router(shopping_fsm_router)
dp.include_router(cart_router)
dp.include_router(order_fsm_router)
dp.include_router(faq_fsm_router)


async def main():
    logging.basicConfig(filename='/app/logs/bot.log', level=logging.INFO)  # Настройка уровня логирования на INFO

    try:
        await bot.set_my_commands([BotCommand(command='start', description='(пере)запустить бота')],
                                  BotCommandScopeDefault())
        await bot(DeleteWebhook(drop_pending_updates=True))  # Удаление вебхука бота с отложенными обновлениями
        await dp.start_polling(bot)  # Запуск опроса бота через диспетчер
    finally:
        await bot.session.close()  # Закрытие сессии бота


if __name__ == "__main__":
    asyncio.run(main())  # Запуск основной функции asyncio при запуске скрипта

from aiogram import Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.types import BotCommand, BotCommandScopeDefault
import asyncio
import logging
import aioredis
import async_timeout

from middlewares.subscription import SubscriptionCallbackMiddleware
from bot import bot, bot_send_mailings
from fsm.faq import faq_fsm_router
from fsm.ordering import order_fsm_router
from fsm.product_quantity import shopping_fsm_router
from handlers.cart import cart_router
from handlers.shopping import shopping_router
from handlers.start import start_command_router
from config_reader import config

dp = Dispatcher()

dp.include_router(start_command_router)
dp.include_router(shopping_router)
dp.include_router(shopping_fsm_router)
dp.include_router(cart_router)
dp.include_router(order_fsm_router)
dp.include_router(faq_fsm_router)
dp.callback_query.outer_middleware(SubscriptionCallbackMiddleware())

STOPWORD = 'STOP'


async def subscribe_to_channel(channel_name):
    redis_url = f'{config.redis_host.get_secret_value()}:{config.redis_port.get_secret_value()}'
    redis = aioredis.Redis.from_url(
        f"redis://{redis_url}", decode_responses=True
    )
    psub = redis.pubsub()

    async def reader(channel: aioredis.client.PubSub):
        while True:
            try:
                async with async_timeout.timeout(5):  # Increase timeout value
                    message = await channel.get_message(ignore_subscribe_messages=True)
                    if message is not None:
                        if message["data"] == STOPWORD:
                            break
                        else:
                            await bot_send_mailings(message["data"])
                    await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass  # Continue listening even if there's a timeout
            except Exception as e:
                logging.error(f"Error in reader: {e}")

    try:
        async with psub as p:
            await p.subscribe(channel_name)
            await reader(p)  # wait for reader to complete
    finally:
        await psub.close()  # Close pubsub connection
        await redis.close()  # Close Redis connection


async def main():
    try:
        logging.basicConfig(filename='/app/logs/bot.log', level=logging.INFO)
        await bot.set_my_commands([BotCommand(command='start', description='(пере)запустить бота')],
                                  BotCommandScopeDefault())
        await bot(DeleteWebhook(drop_pending_updates=True))

        # Start listening to the Redis channel and bot polling concurrently
        listener_task = asyncio.create_task(subscribe_to_channel('mailings'))
        polling_task = asyncio.create_task(dp.start_polling(bot))

        # Wait for both tasks to complete
        await listener_task
        await polling_task
    finally:
        # Close bot session after all tasks are completed
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

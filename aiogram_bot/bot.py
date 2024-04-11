from config_reader import config
from aiogram import Bot

bot = Bot(token=config.bot_token.get_secret_value())

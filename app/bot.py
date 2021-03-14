import os
import logging
from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv

from app.dialogs import greetings_messages, msg
from database import database as db


dotenv_token_path = os.path.join(os.path.dirname(__file__), '../.env')

if os.path.exists(dotenv_token_path):
    load_dotenv(dotenv_token_path)

TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler()
async def test_message(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(msg.test.format(name=user_name))


async def on_shutdown(dp):
    logging.warning('Shutting down...')
    # Закрытие соединения с базой данных
    db._conn.close()
    logging.warning('DB connection closed')

import os
import logging
from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv

import app.service as s
from app.dialogs import msg
from database import cache, database as db
from config import YEAR, MINUTE


dotenv_token_path = os.path.join(os.path.dirname(__file__), '../.env')

if os.path.exists(dotenv_token_path):
    load_dotenv(dotenv_token_path)

TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    """Обработка команды start. Вывод текста и меню"""
    user_currency_ids = await s.get_currency_ids(message.from_user.id)
    if not user_currency_ids:
        await message.answer(msg.start_new_user)
        # Добавления id сообщения настроек
        cache.setex(f'last_msg_{message.from_user.id}', YEAR, message.message_id+2)
        await set_or_update_config(user_id=message.from_user.id)
    else:
        await message.answer(msg.start_current_user, reply_markup=s.MAIN_KB)


@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    """Обработка команды help. Вывод текста и меню"""
    await message.answer(msg.help, reply_markup=s.MAIN_KB)


@dp.callback_query_handler(lambda c: c.data == 'main_window')
async def show_main_window(callback_query: types.CallbackQuery):
    """Главный экран"""
    await callback_query.answer()
    await bot.send_message(callback_query.from_user.id, msg.main, reply_markup=s.MAIN_KB)


@dp.message_handler(lambda message: message.text == msg.btn_online)
@dp.message_handler(commands=['online'])
async def get_results(message: types.Message):
    """Обработка команды ec_today и кнопки Онлайн.
    Запрос курса валют. Вывод результатов"""



@dp.callback_query_handler(lambda c: c.data.startswith('update_results'))
async def update_results():
    """Обновление сообщения результатов"""
    pass


@dp.message_handler(lambda message: message.text == msg.btn_config)
async def get_config(message: types.Message):
    """Обработка кнопки Настройки.
    Проверка выбора лиг. Вывод меню изменений настроек"""
    user_currency_ids = s.get_currency_ids(message.from_user.id)
    if user_currency_ids:
        cache.setex(f'last_msg{message.from_user.id}', YEAR, message.message_id + 2)
        currencies = s.get_currency_names(user_currency_ids)
        await message.answer(msg.config.format(currencies=currencies),
                             reply_markup=s.MAIN_KB)
    else:
        cache.setex(f'last_msg{message.from_user.id}', YEAR, message.message_id + 1)
        await set_or_update_config(user_id=message.from_user.id)


@dp.callback_query_handler(lambda c: c.data.startswith('edit_config'))
async def set_or_update_config(user_id: str):
    """Получение или обновление выбранных лиг"""
    pass


@dp.callback_query_handler(lambda c: c.data[:6] in ['del_le', 'add_le'])
async def update_leagues_info(callback_query: types.CallbackQuery):
    """Добавление/удаление лиги из кеша, обновление сообщения"""
    pass


@dp.callback_query_handler(lambda c: c.data == 'save_config')
async def save_config(callback_query: types.CallbackQuery):
    """Сохранение пользователя в базу данных"""
    pass


@dp.callback_query_handler(lambda c: c.data == 'delete_config')
async def delete_config(callback_query: types.CallbackQuery):
    """Удаление пользователя из базы данных"""
    await db.delete_users(callback_query.from_user.id)
    cache.delete(f"u{callback_query.from_user.id}")
    await callback_query.answer()
    cache.incr(f"last_msg_{callback_query.from_user.id}")
    await bot.send_message(callback_query.from_user.id,
                           msg.data_delete,
                           reply_markup=s.MAIN_KB)


@dp.message_handler()
async def unknown_message(message: types.Message):
    """Ответ на любое неожидаемое сообщение"""
    pass


async def on_shutdown(dp):
    pass


# @dp.message_handler()
# async def test_message(message: types.Message):
#     # имя юзера из настроек Телеграма
#     user_name = message.from_user.first_name
#     await message.answer(msg.test.format(name=user_name))
#
#
# async def on_shutdown(dp):
#     logging.warning('Shutting down...')
#     # Закрытие соединения с базой данных
#     db._conn.close()
#     logging.warning('DB connection closed')

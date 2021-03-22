from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from emoji import emojize
from typing import List

from config import CURRENCIES, CURRENCIES_ENG, MINUTE
from database import cache, database as db
from app.dialogs import msg
from get_currency import fetch_all_currencies, result, exchange_ratio

MAIN_KB = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).row(KeyboardButton(msg.btn_ec_today),
      KeyboardButton(msg.btn_config)
      )

CONFIG_KB = InlineKeyboardMarkup().row(
    InlineKeyboardButton(msg.btn_back, callback_data='main_window'),
    InlineKeyboardButton(msg.config_btn_edit, callback_data='edit_config#')
).add(InlineKeyboardButton(msg.config_btn_delete, callback_data='delete_config'))


async def get_currency_ids(user_id: int):
    currencies = cache.lrange(f'u{user_id}', 0, -1)
    if currencies is None:
        currencies = await db.select_users(user_id)
        if currencies is not None:
            currencies = currencies.split(',')
            [cache.lpush(f'u{user_id}', curr_id) for curr_id in currencies]
        else:
            return []
    print(currencies)
    return currencies


def currencies_kb(active_currencies: list, offset: int = 0):
    kb = InlineKeyboardMarkup()
    currencies_keys = list(CURRENCIES.keys())[0+offset:5+offset]
    for curr_id in currencies_keys:
        if curr_id in active_currencies:
            kb.add(
                InlineKeyboardButton(
                    f'{emojize(":white_heavy_check_mark:")} {CURRENCIES[curr_id][0]}',
                    callback_data=f'del_currency_#{offset}#{curr_id}'
                )
            )
        else:
            kb.add(
                InlineKeyboardButton(
                    CURRENCIES[curr_id][0],
                    callback_data=f'add_currency_#{offset}#{curr_id}'
                )
            )
    kb.row(
        InlineKeyboardButton(
            msg.btn_back if offset else msg.btn_go,
            callback_data='edit_config#0' if offset else 'edit_config#5'),
        InlineKeyboardButton(
            msg.btn_save, callback_data='save_config'
        )
    )
    return kb


async def get_currency_names(ids: list) -> str:
    """Функция собирает сообщение с названиями валют из id"""
    currencies_text = ''
    for i, curr_id in enumerate(ids, start=1):
        if i != 1:
            currencies_text += '\n'
        currencies_text += msg.currency_row.format(
            i=i,
            name=CURRENCIES.get(curr_id, '-')[0]
        )
    return currencies_text


def update_currencies(user_id: int, data: str):
    currency_id = data.split('#')[-1]
    if data.startswith('add'):
        cache.lpush(f'u{user_id}', currency_id)
    else:
        cache.lrem(f'u{user_id}', 0, currency_id)


def results_kb(currencies: list):
    params = [f"#{curr}" for curr in currencies]
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        msg.update_results,
        callback_data=f"update_results{''.join(params)}"
    ))
    return kb


async def generate_results_answer(ids: list) -> str:
    """Функция создaет сообщение для вывода валютных курсов"""
    results = await get_last_results(ids)
    if results == [[]]*len(ids):
        return msg.no_results
    elif msg.fetch_error in results:
        return msg.fetch_error
    else:
        text_results = results_to_text(results)
        return msg.results.format(last_currencies=text_results)


def ids_to_key(ids: list) -> str:
    """Стандартизация ключей для хранения курсов"""
    ids.sort()
    return ",".join(ids)


async def parse_currencies() -> dict:
    """Функция получения данных по валютам по API"""
    data = {}
    currencies = fetch_all_currencies()
    if currencies.get("error", False):
        return currencies

    for curr, value in currencies.items():
        data[curr] = currencies[curr]
        # if not data.get(str(curr['currency_id']), False):
        #     data[curr] = [value[0] + ' ' + value[1]]
        # else:
        #     data[curr].append(curr)
    return data


async def save_currencies(currencies: dict):
    for curr_id in CURRENCIES.keys():
        cache.jset(curr_id, currencies.get(curr_id, []), MINUTE)


async def get_last_results(currencies_ids: list) -> List[dict]:
    last_currencies = [cache.jget(curr_id) for curr_id in currencies_ids]
    currencies_names = [CURRENCIES.get(curr_id)[1] for curr_id in currencies_ids]
    if None in last_currencies:
        all_currencies = await parse_currencies()
        chosen_currencies = {}
        for curr in all_currencies.keys():
            if curr in currencies_names:
                chosen_currencies[curr] = all_currencies[curr]
        if chosen_currencies.get('error', False):
            # добавляем новые данные по валютам, если они есть
            return msg.fetch_error
        else:
            await save_currencies(chosen_currencies)
            last_currencies = [{curr_name: chosen_currencies.get(curr_name, []) for curr_name in currencies_names}]
    return last_currencies


def results_to_text(currencies: list) -> str:
    """
    Функция генерации сообщения с данными по валютам
    """
    text = ''
    for currency, value in currencies[0].items():
        text += 'Курс ' + CURRENCIES_ENG[currency] + f': {str(value)} ' + exchange_ratio[currency] + '\n'
    return text


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from emoji import emojize
from config import CURRENCIES
from database import cache, database as db
from app.dialogs import msg

MAIN_KB = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True
).row(KeyboardButton(msg.btn_ec_today),
      KeyboardButton(msg.btn_config)
      )


async def get_currency_ids(user_id: int):
    currencies = cache.lrange(f'u{user_id}', 0, -1)
    if currencies is None:
        currencies = await db.select_users(user_id)
        if currencies is not None:
            currencies = currencies.split(',')
            [cache.lpush(f'u{user_id}', lg_id) for lg_id in currencies]
        else:
            return []
    return  currencies


CONFIG_KB = InlineKeyboardMarkup().row(
    InlineKeyboardButton(msg.btn_back, callback_data='main_window'),
    InlineKeyboardButton(msg.btn_edit, callback_data='edit_config#')
).add(InlineKeyboardButton(msg.config_btn_delete, callback_data='delete_config'))


def currencies_kb(active_currencies: list, offset: int = 0):
    kb = InlineKeyboardMarkup()
    currencies_keys = list(CURRENCIES.keys())[0+offset:5+offset]
    for cur_id in currencies_keys:
        if cur_id in active_currencies:
            kb.add(
                InlineKeyboardButton(
                    f'{emojize(":white_heavy_check_mark:")} {CURRENCIES[cur_id]}',
                    callback_data=f'del_currency_#{offset}#{cur_id}'
                )
            )
        else:
            kb.add(
                InlineKeyboardButton(
                    CURRENCIES[cur_id],
                    callback_data=f'add_currency_#{offset}#{cur_id}'
                )
            )
    kb.row(
        InlineKeyboardButton(
            msg.btn_back if offset else msg.button_go,
            callback_data='edit_config#0' if offset else 'edit_config#5'),
        InlineKeyboardButton(
            msg.btn_save, callback_data='save_config'
        )
    )
    return kb


async def get_currency_names(ids: list) -> str:
    """Функция собирает сообщение с названиями лиг из id"""
    currencies_text = ''
    for i, curr_id in enumerate(ids, start=1):
        if i != 1:
            currencies_text += '\n'
        currencies_text += msg.currency_row.format(
            i=i,
            name=CURRENCIES.get(curr_id, '-')
        )
    return currencies_text


def update_currencies(user_id: int, data: str):
    currency_id = data.split('#')[-1]
    if data.startswith('add'):
        cache.lpush(f'u{user_id}', currency_id)
    else:
        cache.lrem(f'{user_id}', 0, currency_id)

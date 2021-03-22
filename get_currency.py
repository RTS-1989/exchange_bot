import requests
import logging
import xml.etree.ElementTree as ET
import datetime
logging.basicConfig(level=logging.INFO)

TODAY = datetime.date.today()
YESTERDAY = TODAY - datetime.timedelta(days=1)
NOW = datetime.datetime.now()
today_15_hours = NOW.replace(hour=15, minute=0, second=0, microsecond=0)
today_14_hours = NOW.replace(hour=14, minute=0, second=0, microsecond=0)
today_12_hours = NOW.replace(hour=12, minute=0, second=0, microsecond=0)
CBRF_API_URL = 'http://www.cbr.ru/scripts/XML_daily.asp?date_req='

months = {
    'январь': '01', 'февраль': '02',
    'март': '03', 'апрель': '04',
    'май': '05', 'июнь': '06',
    'июль': '07', 'август': '08',
    'сентябрь': '09', 'октябрь': '10',
    'ноябрь': '11', 'декабрь': '12'
}

result = {
    'usd': 0,
    'euro': 0,
    'yen': 0,
    'czk': 0,
    'pound_sterling': 0,
    'yuan': 0,
    'zloty': 0,
    'hryvnia': 0
}

exchange_ratio = {
    'usd': 'за 1 доллар',
    'euro': 'за 1 евро',
    'yen': 'за 100 йен',
    'czk': 'за 10 чешских крон',
    'pound_sterling': 'за 1 фунт стерлинга',
    'yuan': 'за 1 юань',
    'zloty': 'за 1 злотый',
    'hryvnia': 'за 10 гривен'
}

currency_structure = {
    'usd': "./*[@ID='R01235']/Value",
    'euro': "./*[@ID='R01239']/Value",
    'yen': "./*[@ID='R01820']/Value",
    'czk': "./*[@ID='R01760']/Value",
    'pound_sterling': "./*[@ID='R01035']/Value",
    'yuan': "./*[@ID='R01375']/Value",
    'zloty': "./*[@ID='R01565']/Value",
    'hryvnia': "./*[@ID='R01720']/Value"
}

currency_messages = {
    'usd': 'Данные по валюте usd еще в процессе изменения, \
на сегодня еще действительны данные за вчерашний день. \nДанные по торгам \
за сегодня будут актуальны в 12:00 (соответство до завтра 12:00) \
по московскому времени.',
    'euro': 'Данные по валюте euro еще в процессе изменения, \
на сегодня еще действительны данные за вчерашний день. \nДанные по торгам \
за сегодня будут актуальны в 14:00 (соответство до завтра 14:00) \
по московскому времени.',
    'other': 'Данные по валюте еще в процессе изменения, \
на сегодня еще действительны данные за вчерашний день. \nДанные по торгам \
за сегодня будут актуальны в 15:00 (соответство до завтра 15:00) \
по московскому времени.'
}


def get_today():
    if TODAY.weekday() not in (5, 6,):
        today = str(TODAY)
        day, month, year = today[-2:], today[-5:-3], today[0:4]
        currency_date = '%s/%s/%s' % (day, month, year)
        logging.info(f'Данные на сегодня: {currency_date}')
        return currency_date
    else:
        if TODAY.weekday() == 5:
            difference = 1
            return get_friday(difference)
        elif TODAY.weekday() == 6:
            difference = 2
            return get_friday(difference)


def get_yesterday():
    if YESTERDAY.weekday() not in (5, 6,):
        yesterday = str(YESTERDAY)
        day, month, year = yesterday[-2:], yesterday[-5:-3], yesterday[0:4]
        currency_date = '%s/%s/%s' % (day, month, year)
        logging.info(f'Данные за вчера: {currency_date}')
        return currency_date
    else:
        if YESTERDAY.weekday() == 5:
            difference = 1
            return get_friday(difference)
        elif YESTERDAY.weekday() == 6:
            difference = 2
            return get_friday(difference)


def get_friday(difference):
    friday = str(TODAY - datetime.timedelta(days=difference))
    day, month, year = friday[-2:], friday[-5:-3], friday[0:4]
    currency_date = '%s/%s/%s' % (day, month, year)
    logging.info(f'Данные на пятницу: {currency_date}')
    return currency_date


def get_date():
    day = input('Введите, пожалуйста день: ')
    month = input('Введите, пожалуйста месяц: ')
    year = int(input('Введите, пожалуйста год: '))

    if month in months.keys():
        month = months[month]
    if year > 0 and year < 91:
        year += 2000

    currency_date = '%s/%s/%s' % (day, month, str(year))

    return currency_date


def get_info(CBRF_API_URL, currency_date):
    info = requests.get(CBRF_API_URL+currency_date)
    return info.content


def get_moscow_time():
    delta = datetime.timedelta(hours=3)
    moscow_time = datetime.datetime.now(datetime.timezone.utc) + delta
    moscow_time = datetime.datetime.strptime(moscow_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    return moscow_time


def time_comparison(currency_name: str) -> bool:
    moscow_time = get_moscow_time()
    if currency_name == 'usd':
        return bool(moscow_time >= today_12_hours)
    elif currency_name == 'euro':
        return bool(moscow_time >= today_14_hours)
    else:
        return bool(moscow_time >= today_15_hours)


# structure = ET.fromstring(get_info(CBRF_API_URL, get_date()))
# dollar = structure.find("./*[@ID='R01235']/Value")
# euro = structure.find("./*[@ID='R01239']/Value")


# def get_usd_currency():
#     result['usd'] = dollar.text.replace(',', '.')
#     return result['usd']
#
#
# def get_euro_currency():
#     result['euro'] = euro.text.replace(',', '.')
#     return result['euro']


def get_currency_today(currency_name: str) -> float:
    if time_comparison(currency_name):
        structure = ET.fromstring(get_info(CBRF_API_URL, get_today()))
        find_currency = structure.find(currency_structure[currency_name])
        result[currency_name] = float(find_currency.text.replace(',', '.'))
        return result[currency_name]
    else:
        if currency_name == 'usd' or currency_name == 'euro':
            logging.info(currency_messages[currency_name])
        else:
            logging.info(currency_messages['other'])
        return get_currency_yesterday(currency_name)


def get_currency_yesterday(currency_name: str) -> float:
    structure = ET.fromstring(get_info(CBRF_API_URL, get_yesterday()))
    find_currency = structure.find(currency_structure[currency_name])
    result[currency_name] = float(find_currency.text.replace(',', '.'))
    logging.info(f'Данные по {currency_name} за {get_yesterday()}')
    return result[currency_name]


def get_currency_actual(currency_name: str) -> tuple:
    structure = ET.fromstring(get_info(CBRF_API_URL, get_today()))
    find_currency = structure.find(currency_structure[currency_name])
    result[currency_name] = find_currency.text.replace(',', '.')
    print(type(result[currency_name]))
    return result[currency_name], exchange_ratio[currency_name]


def fetch_all_currencies() -> dict:
    for curr in result.keys():
        result[curr] = get_currency_today(curr)
    return result


if __name__ == '__main__':
    start = datetime.datetime.now()
    print(type(get_currency_today('czk')))
    # print(get_currency_yesterday('euro'))
    # print(get_moscow_time())
    print(get_currency_actual('usd'))
    # print(fetch_all_currencies())
    end = datetime.datetime.now()
    result = end - start
    print(result)

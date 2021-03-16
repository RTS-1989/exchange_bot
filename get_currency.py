import requests
import logging
import xml.etree.ElementTree as ET
from datetime import date, timedelta

logging.basicConfig(level=logging.INFO)

TODAY = date.today()
YESTERDAY = TODAY - timedelta(days=1)
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
    'czech': 0,
    'pound_sterling': 0,
    'yuan': 0,
    'zloty': 0,
    'hryvnia': 0
}

exchange_ratio = {
    'to_usd': 'for 1 usd',
    'to_euro': 'for 1 euro'
}

currency_structure = {
    'usd': "./*[@ID='R01235']/Value",
    'euro': "./*[@ID='R01239']/Value",
    'yen': "./*[@ID='R01820']/Value",
    'czech': "./*[@ID='R01760']/Value",
    'pound_sterling': "./*[@ID='R01035']/Value",
    'yuan': "./*[@ID='R01375']/Value",
    'zloty': "./*[@ID='R01565']/Value",
    'hryvnia': "./*[@ID='R01720']/Value"
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
        day, month, year = YESTERDAY[-2:], YESTERDAY[-5:-3], YESTERDAY[0:4]
        currency_date = '%s/%s/%s' % (day, month, year)
        return currency_date
    else:
        if YESTERDAY.weekday() == 5:
            difference = 1
            return get_friday(difference)
        elif YESTERDAY.weekday() == 6:
            difference = 2
            return get_friday(difference)


def get_friday(difference):
    friday = str(TODAY - timedelta(days=difference))
    day, month, year = friday[-2:], friday[-5:-3], friday[0:4]
    currency_date = '%s/%s/%s' % (day, month, year)
    logging.info(f'Данные на пятницу {currency_date}')
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
    get_info = requests.get(CBRF_API_URL+currency_date)
    return get_info.content


# structure = ET.fromstring(get_info(CBRF_API_URL, get_date()))
# dollar = structure.find("./*[@ID='R01235']/Value")
# euro = structure.find("./*[@ID='R01239']/Value")


def get_usd_currency():
    result['usd'] = dollar.text.replace(',', '.')
    return result['usd']


def get_euro_currency():
    result['euro'] = euro.text.replace(',', '.')
    return result['euro']


def get_currency_today(currency_name: str):
    structure = ET.fromstring(get_info(CBRF_API_URL, get_today()))
    find_currency = structure.find(currency_structure[currency_name])
    if find_currency is None:
        structure = ET.fromstring(get_info(CBRF_API_URL, get_yesterday()))
        find_currency = structure.find(currency_structure[currency_name])
        result[currency_name] = find_currency.text.replace(',', '.')
        return result[currency_name]
    result[currency_name] = find_currency.text.replace(',', '.')
    return result[currency_name]


if __name__ == '__main__':
    # print(get_date())
    # print(get_usd_currency()),
    # print(get_euro_currency()),
    # print(date.today() - timedelta(days=1)),
    print(get_currency_today('hryvnia'))
    # print(get_yesterday())
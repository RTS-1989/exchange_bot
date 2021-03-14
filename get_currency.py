import requests
import xml.etree.ElementTree as ET


url = 'http://www.cbr.ru/scripts/XML_daily.asp?date_req='
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
    'euro': 0
}


def get_date():
    day = input('Введите, пожалуйста день: ')
    month = input('Введите, пожалуйста месяц: ')
    year = int(input('Введите, пожалуйста год: '))

    if month in months.keys():
        month = months[month]
    if year > 0 and year < 91:
        year += 2000

    date = '%s/%s/%s' % (day, month, str(year))

    return date


def get_info(url, date):
    get_info = requests.get(url+date)
    return get_info.content


structure = ET.fromstring(get_info(url, get_date()))
dollar = structure.find("./*[@ID='R01235']/Value")
euro = structure.find("./*[@ID='R01239']/Value")


def get_usd_currency():
    result['usd'] = dollar.text.replace(',', '.')
    return result['usd']


def get_euro_currency():
    result['euro'] = euro.text.replace(',', '.')
    return result['euro']


if __name__ == '__main__':
    print(get_usd_currency()),
    print(get_euro_currency())
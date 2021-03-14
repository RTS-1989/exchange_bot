import os
import logging
import sqlite3
import redis
import ujson
from dotenv import load_dotenv

# import config

logging.basicConfig(level=logging.INFO)


dotenv_token_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_token_path):
    load_dotenv(dotenv_token_path)


class Cache(redis.StrictRedis):
    def __init__(self, host, port, password,
                 charset='utf-8',
                 decode_responses=True):
        super(Cache, self).__init__(host, port,
                            password=password,
                            charset=charset,
                            decode_responses=decode_responses)
        logging.info('Redis start')

    def jset(self, name, value, ex=2):
        '''функция конвертирует python-объект в Json и сохранит'''
        r = self.get(name)
        if r is None:
            return r
        return ujson.load(r)

    def jget(self, name):
        """функция возвращает Json и конвертирует в python-объект"""
        return ujson.loads(self.get(name))


class Database:
    def __init__(self, name):
        self.name = name
        self._conn = self.connection()
        logging.info("Database connection established")

    def create_db(self):
        connection = sqlite3.connect(f'{self.name}.db')
        logging.info('Database created')
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS currency_info
        (id INT AUTO_INCREMENT,
        currency_id INT,
        currency_value INT NULL,
        date DATE NOT NULL,
        FOREIGN KEY (currency_id) REFERENCES currency (id),
        PRIMARY KEY (id));
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS currency
        (id INT AUTO_INCREMENT,
        currency_name VARCHAR(30) NOT NULL,
        PRIMARY KEY (id));
        ''')
        connection.commit()
        cursor.close()

    def connection(self):
        db_path = os.path.join(os.getcwd(), f'{self.name}.db')
        if not os.path.exists(db_path):
            self.create_db()
        return sqlite3.connect(f'{self.name}.db')

    def _execute_query(self, query, select=False):
        cursor = self._conn.cursor()
        cursor.execute(query)
        if select:
            records = cursor.fetchone()
            cursor.close()
            return records
        else:
            self._conn.commit()
        cursor.close()

    async def insert_currency(self, currency_name: str):
        insert_query = f'''INSERT INTO currency(currency_name)
                                        VALUES("{currency_name}")'''
        self._execute_query(insert_query)
        logging.info(f'{currency_name} was add in table currency')

    async def insert_currency_value(self, currency_name: str, currency_value: int, date):
        currency_id = f'''SELECT id FROM currency
                                WHERE currency_name = "{currency_name}"'''
        insert_query = f'''INSERT INTO currency_info(currency_id, currency_value,
                            date) VALUES({currency_id}, {currency_value},
                            "{date}")'''
        self._execute_query(insert_query)
        logging.info(f'{currency_name} on {date} was added to db with '
                     f'value = {currency_value}')

    async def select_currency(self, currency_name: str):
        select_query = f'''SELECT currency_name FROM currency
                        WHERE currency_name = "{currency_name}" LIMIT 1'''
        record = self._execute_query(select_query, select=True)
        return record

    async def select_currency_value(self, currency_name: str, date):
        currency_id = f'''SELECT id FROM currency
                        WHERE currency_name = "{currency_name}"'''
        select_query = f'''SELECT (SELECT currency_name FROM currency
                        WHERE currency_id = {currency_id}) AS currency_name, 
                        currency_value, date FROM currency_info
                        WHERE date = "{date}"'''
        record = self._execute_query(select_query, select=True)
        return record

    async def delete_currency(self, currency_name):
        delete_query = f'''DELETE FROM currency
                        WHERE currency_name = "{currency_name}"'''
        self._execute_query(delete_query)
        logging.info(f'Info about {currency_name} was deleted '
                     f'from currency table')

    async def delete_all_currency_info(self, currency_name):
        currency_id = f'''SELECT id FROM currency
                        WHERE currency_name = "{currency_name}"'''
        delete_query = f'''DELETE FROM currency_info 
                        WHERE currency_id = {currency_id}'''
        self._execute_query(delete_query)
        logging.info(f'Info about {currency_name} was deleted '
                     f'from currency_info table')

    async def delete_currency_info_by_date(self, currency_name, date):
        currency_id = f'''SELECT id FROM currency
                        WHERE currency_name = "{currency_name}"'''
        delete_by_date_query = f'''DELETE FROM currency_info
                        WHERE currency_id = {currency_id} AND
                        date = "{date}"'''
        self._execute_query(delete_by_date_query)
        logging.info(f'Info about {currency_name} for {date} was deleted')


cache = Cache(
    host = os.getenv('REDIS_HOST'),
    port = os.getenv('REDIS_PORT'),
    password = os.getenv('REDIS_PASSWORD')
)

database = Database(os.getenv('BOT_DB_NAME'))

# cache = Cache(
#     host=config.REDIS_HOST,
#     port=config.REDIS_PORT,
#     password=config.REDIS_PASSWORD
# )
# database = Database(config.BOT_DB_NAME)

import os
import logging
import sqlite3
import redis
import ujson
from dotenv import load_dotenv
from datetime import date

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

    def jset(self, name, value, ex=0):
        """функция конвертирует python-объект в Json и сохранит"""
        return self.setex(name, ex, ujson.dumps(value))

    def jget(self, name):
        """функция возвращает Json и конвертирует в python-объект"""
        r = self.get(name)
        if r is None:
            return r
        return ujson.loads(r)



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
        currency_name VARCHAR(30) NOT NULL,
        currency_value INT NULL,
        date DATE NOT NULL,
        PRIMARY KEY (id));
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users
        (id INT PRIMARY KEY,
        currency_name VARCHAR(30) NOT NULL);
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

    async def insert_users(self, user_id: int, currency_name: str):
        insert_query = f'''INSERT INTO users(id, currency_name)
                            VALUES({user_id}, "{currency_name}")'''
        self._execute_query(insert_query)
        logging.info(f'{user_id} with {currency_name} was added to users table')

    async def insert_currency_value(self, currency_name: str, currency_value: int, currency_date):
        insert_query = f'''INSERT INTO currency_info(currency_name, currency_value,
                            date) VALUES("{currency_name}", {currency_value},
                            "{currency_date}")'''
        self._execute_query(insert_query)
        logging.info(f'{currency_name} on {currency_date} was added to db with '
                     f'value = {currency_value}')

    async def update_users(self, user_id, currency_name):
        update_query = f'''UPDATE users SET currency_name = "{currency_name}"
                        WHERE user_id = {user_id}'''
        self._execute_query(update_query)
        logging.info(f'Currencies for user {user_id} was updated')

    async def insert_or_update(self, user_id: int, currencies: str):
        user_currencies = await self.select_users(user_id)
        if user_currencies is not None:
            await self.update_users(user_id, currencies)
        else:
            await self.insert_users(user_id, currencies)

    async def select_users(self, user_id: int):
        select_query = f'''SELECT currency_name FROM users
                        WHERE id = {user_id}'''
        record = self._execute_query(select_query, select=True)
        return record

    async def select_currency_value(self, currency_name: str, currency_date):
        select_query = f'''SELECT currency_name,
                        currency_value, date FROM currency_info
                        WHERE currency_name = "{currency_name}" AND 
                        date = "{currency_date}"'''
        record = self._execute_query(select_query, select=True)
        return record

    async def delete_users(self, user_id: int):
        delete_query = f'''DELETE FROM users
                        WHERE id = {user_id}'''
        self._execute_query(delete_query)
        logging.info(f'{user_id} was deleted from users')

    async def delete_all_currency_info(self, currency_name):
        delete_query = f'''DELETE FROM currency_info 
                        WHERE currency_name = "{currency_name}"'''
        self._execute_query(delete_query)
        logging.info(f'Info about {currency_name} was deleted '
                     f'from currency_info table')

    async def delete_currency_info_by_date(self, currency_name, currency_date):
        delete_by_date_query = f'''DELETE FROM currency_info
                        WHERE currency_name = "{currency_name}" AND
                        date = "{currency_date}"'''
        self._execute_query(delete_by_date_query)
        logging.info(f'Info about {currency_name} for {currency_date} was deleted')


cache = Cache(
    host=os.getenv('REDIS_HOST'),
    port=os.getenv('REDIS_PORT'),
    password=os.getenv('REDIS_PASSWORD')
)

database = Database(os.getenv('BOT_DB_NAME'))

# cache = Cache(
#     host=config.REDIS_HOST,
#     port=config.REDIS_PORT,
#     password=config.REDIS_PASSWORD
# )
# database = Database(config.BOT_DB_NAME)

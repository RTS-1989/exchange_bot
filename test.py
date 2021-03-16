import unittest
import aiohttp
from unittest import IsolatedAsyncioTestCase

from database import cache, database
from app import bot, service


class TestDatabase(IsolatedAsyncioTestCase):
    async def test_crud(self):
        await database.insert_users(1111, 'euro')
        self.assertEqual(await database.select_users(1111), ('euro',))
        await database.delete_users(1111)
        self.assertEqual(await database.delete_users(1111), None)
        await database.insert_currency_value('euro', 88, '2021-3-10')
        self.assertEqual(await database.select_currency_value('euro', '2021-3-10'), ('euro', 88, '2021-3-10',))
        await database.delete_all_currency_info('euro')
        self.assertEqual(await database.select_currency_value('euro', '2021-3-10'), None)
        await database.insert_currency_value('usd', 71, '2020-9-10')
        await database.insert_currency_value('euro', 81, '2020-9-11')
        self.assertEqual(await database.delete_currency_info_by_date('usd', '2020-9-10'), None)
        self.assertEqual(await database.select_currency_value('euro', '2020-9-11'), ('euro', 81, '2020-9-11',))
        self.assertEqual(await database.delete_currency_info_by_date('euro', '2020-9-11'), None)


class TestCache(unittest.TestCase):
    def test_connection(self):
        self.assertTrue(cache.ping())

    def test_response_type(self):
        cache.setex("test_type", 10, "Hello")
        response = cache.get("test_type")
        self.assertEqual(type(response), str)


class TestBot(IsolatedAsyncioTestCase):
    async def test_bot_auth(self):
        bot.bot._session = aiohttp.ClientSession()
        bot_info = await bot.bot.get_me()
        await bot.bot._session.close()

        self.assertEqual(bot_info["username"], "rts1989_currency_bot")


class TestService(IsolatedAsyncioTestCase):
    async def test_get_currency_ids(self):
        ids = await service.get_currency_ids("1111")
        self.assertEqual(type(ids), list)

    async def test_get_last_results(self):
        results = await service.get_last_results(["1", "2", "3"])
        self.assertEqual(type(results), list)


if __name__ == '__main__':
    unittest.main()
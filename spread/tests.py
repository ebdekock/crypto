import inspect
import types
from django.conf import settings
from django.test import TestCase
from django.test import LiveServerTestCase
from spread.models import Price
from spread.models import Exchange_rate
import spread.convert_currency
import spread.exchanges

# Create site URL for tests
site_url = 'http://' + settings.SITE_URL + ":" + settings.SITE_PORT

class IndexTest(TestCase):

    def setUp(self):
        """Set up simple base entries for index test."""
        Exchange_rate.objects.create(currency="USDZAR", price=14)
        Price.objects.create(exchange="Luno", price=10, volume=5, currency="Bitcoin")
        Price.objects.create(exchange="Luno", price=9, volume=5, currency="Bitcoin")
        Price.objects.create(exchange="Bittrex", price=5, volume=5, currency="Bitcoin")
        Price.objects.create(exchange="Bittrex", price=4, volume=5, currency="Bitcoin")

    def test_uses_correct_template(self):
        response = self.client.get(site_url)
        self.assertTemplateUsed(response, 'spread/index.html')

class CronTest(TestCase):

    def setUp(self):
        """Set up currency lookup for exchange tests."""
        Exchange_rate.objects.create(currency="USDZAR", price=14)

    def test_currency_return_types(self):
        """ Make sure currency crons returns correct types, if any results."""
        currency_conversions = inspect.getmembers(spread.convert_currency, inspect.isfunction)
        self.assertIs(type(currency_conversions), list)

        for currency_api_lookup in currency_conversions:
            self.assertIs(type(currency_api_lookup), tuple)
            self.assertIs(type(currency_api_lookup[0]), str)
            self.assertTrue(callable(currency_api_lookup[1]))
            result = None
            result = currency_api_lookup[1]()
            if result:
                self.assertIs(type(result), dict)
                for currency, price in result.items():
                    self.assertIs(type(currency), str)
                    self.assertIs(type(price), float)

    def test_exchange_return_types(self):
        """ Make sure exchange crons returns correct types, if any results."""
        list_of_exchanges = inspect.getmembers(spread.exchanges, inspect.isfunction)
        self.assertIs(type(list_of_exchanges), list)

        for exchange_api_lookup in list_of_exchanges:
            self.assertIs(type(exchange_api_lookup), tuple)
            result = None
            result = exchange_api_lookup[1]()
            if result:
                self.assertIs(type(result), dict)
                for exchange, data in result.items():
                    self.assertIs(type(exchange), str)
                    self.assertIs(type(data), dict)
                    self.assertIs(type(data['currency']), str)
                    self.assertIs(type(data['price']), float)
                    self.assertIs(type(data['volume']), float)






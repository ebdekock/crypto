import sys
import inspect
import logging
import spread.convert_currency
import spread.exchanges
from spread.models import Price
from spread.models import Exchange_rate
from django.utils import timezone

# Create logger instance
logger = logging.getLogger(__name__)

def currency_lookup():
    """ Go through all currency conversions defined in spread.convert_currency, do lookups."""
    # Create tuple of all convert functions:
    # [('usd_to_zar', <function usd_to_zar>), ]
    currency_conversions = inspect.getmembers(spread.convert_currency, inspect.isfunction)

    for currency_api_lookup in currency_conversions:
        result = None
        # Run function
        result = currency_api_lookup[1]()
        # Parse results if successul
        if result:
            for key in result:
                try:
                    # If this currency already exists, update new price
                    latest = Exchange_rate.objects.get(currency=key)
                    latest.price = result[key]
                    latest.date = timezone.now()
                    latest.save()
                except Exchange_rate.DoesNotExist:
                    latest = Exchange_rate()
                    latest.currency = str(key)
                    latest.price = result[key]
                    latest.save()

def price_lookup():
    """Go through all exchange lookups defined in spread.exchanges, do lookups."""
    # Create tuple of all convert functions:
    # [('luno', <function luno>), ]
    list_of_exchanges = inspect.getmembers(spread.exchanges, inspect.isfunction)

    for exchange_api_lookup in list_of_exchanges:
        result = None
        # Run function
        result = exchange_api_lookup[1]()
        # Parse results if successul
        if result:
            for key in result:
                try:
                    p = Price()
                    p.exchange = str(key)
                    p.price = result[key]["price"]
                    p.volume = result[key]["volume"]
                    p.currency = result[key]["currency"]
                    p.save()
                except (KeyboardInterrupt, SystemExit):
                    sys.exit(1)
                except Exception as error:
                    logger.warning(error)
                    pass

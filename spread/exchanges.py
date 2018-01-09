import requests
import logging
from spread.models import Exchange_rate

# def example_exchange():
#     """ 
#     Exchange price lookup. All functions in this file will be run, can simply add additional exchanges.
#     When removing an exchange, you must remove all database entries as well. 
#     Must return None or Dictionary: { exchange: {"currency": currency, "price": price, "volume": volume }}
#     Types - see Models 
#     exchange - Price.exchange
#     currency - Price.currency
#     price - Price.price
#     volume - Price.volume (must be bitcoin volume in last 24 hours)
#     """
#     exchange = "Exchange"
#     currency = "Crypto"
#     api_url = "https://example.co.za"
#     try:
#         exchange_lookup = requests.get(api_url)
#         # If successful request and its valid JSON,
#         # then extract price and volume values, return dictionary.
#         if exchange_lookup.status_code == 200 and exchange_lookup.json():
#             price = exchange_lookup.json()
#             volume = exchange_lookup.json()
#             return { exchange: {"currency": currency, "price": price, "volume": volume }}
#         else:
#             return None
#     except Exception as error:
#         # We do not care at all that this request fails, simply log error.
#         # If it gets data - great - if it doesn't, graphs will simply be slightly less accurate.
#         logger.error(error)
#         return None

# Create logger instance
logger = logging.getLogger(__name__)

def luno() -> ExchangeData:
    exchange = "Luno"
    currency = "Bitcoin"
    api_url = "https://api.mybitx.com/api/1/ticker?pair=XBTZAR"

    try:
        luno_lookup = requests.get(api_url)
        if luno_lookup.status_code == 200 and luno_lookup.json():
            price = float(luno_lookup.json()["last_trade"])
            volume = float(luno_lookup.json()["rolling_24_hour_volume"])
            return { exchange: {"currency": currency, "price": price, "volume": volume }}
        else:
            return None
    except Exception as error:
        logger.warning(error)
        return None

def bitfinex():
    exchange = "Bitfinex"
    currency = "Bitcoin"
    exchange_rate = Exchange_rate.objects.get(currency="USDZAR")
    api_url = "https://api.bitfinex.com/v1/pubticker/btcusd"

    try:
        bitfinex_lookup = requests.get(api_url)
        if bitfinex_lookup.status_code == 200 and bitfinex_lookup.json():
            price = float(bitfinex_lookup.json()["last_price"]) * float(exchange_rate.price)
            volume = float(bitfinex_lookup.json()["volume"])
            return { exchange: {"currency": currency, "price": price, "volume": volume }}
        else:
            return None
    except Exception as error:
        logger.warning(error)
        return None

def gdax():
    exchange = "GDAX"
    currency = "Bitcoin"
    exchange_rate = Exchange_rate.objects.get(currency="USDZAR")
    api_url = "https://api.gdax.com/products/BTC-USD/ticker"

    try:
        gdax_lookup = requests.get(api_url)
        if gdax_lookup.status_code == 200 and gdax_lookup.json():
            price = float(gdax_lookup.json()["price"]) * float(exchange_rate.price)
            volume = float(gdax_lookup.json()["volume"])
            return { exchange: {"currency": currency, "price": price, "volume": volume }}
        else:
            return None
    except Exception as error:
        logger.warning(error)
        return None

def bittrex():
    # Technically not USD, its tether, which "should" be 1:1 with USD
    exchange = "Bittrex"
    currency = "Bitcoin"
    exchange_rate = Exchange_rate.objects.get(currency="USDZAR")
    api_url = "https://bittrex.com/api/v1.1/public/getmarketsummary?market=USDT-BTC"

    try:
        bittrex_lookup = requests.get(api_url)
        if bittrex_lookup.status_code == 200 and bittrex_lookup.json():
            price = float(bittrex_lookup.json()["result"][0]["Last"]) * float(exchange_rate.price)
            volume = float(bittrex_lookup.json()["result"][0]["Volume"])
            return { exchange: {"currency": currency, "price": price, "volume": volume }}
        else:
            return None
    except Exception as error:
        logger.warning(error)
        return None

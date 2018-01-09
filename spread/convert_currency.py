import requests
import logging
from django.conf import settings

# def example_convert():
#     """ 
#     Currency conversion. All functions in this file will be run.
#     Must return either None or Dictionary with the format: { conversion: exchange_rate}
#     Types - see Models: 
#     conversion - Exchange_rate.currency, exchange_rate - Exchange_rate.price
#     """
#
#     # Convert from - to.
#     conversion = "USDZAR"
#     api_url = "http://example.co.za"
#     try:
#         currency_lookup = requests.get(api_url)
#         # If successful request and its valid JSON, then extract rate and return value.
#         if currency_lookup.status_code == 200 and currency_lookup.json():
#             exchange_rate = currency_lookup.json()['rates']['ZAR']
#             return { conversion: exchange_rate}
#         else:
#             return None
#     except Exception as error:
#         # We do not care at all that this request fails, simply log error.
#         # If it gets data - great - if it doesn't, exchange rate data will be slightly outdated.
#         logger.error(error)
#         return None

# Create logger instance
logger = logging.getLogger(__name__)

def usd_to_zar():
    # Should limit to one per hour, free account only has 1000 API lookups/month
    conversion = "USDZAR"
    api_url = "https://openexchangerates.org/api/latest.json?symbols=ZAR&app_id=" + settings.CONVERT_CURRENCY_API_KEY
    try:
        currency_lookup = requests.get(api_url)
        if currency_lookup.status_code == 200 and currency_lookup.json():
            exchange_rate = currency_lookup.json()['rates']['ZAR']
            return { conversion: exchange_rate}
        else:
            return None
    except Exception as error:
        logger.warning(error)
        return None

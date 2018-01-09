import math
import os
import logging
from collections import OrderedDict
from datetime import timedelta
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.db.models import Min
from django.db.models import Max
from django.db.models import Avg
from django.utils import timezone
from django.db.utils import OperationalError
from spread.models import Price

def index(request):
    """Main index page of site."""

    # Number of days to display on graphs
    RANGE_OF_DAYS = 14

    # Database lookup, if it fails, serve blank template
    data = get_database_data(RANGE_OF_DAYS)
    if not data:
        return render(request, 'spread/index.html')

    # Get line graph data
    line_graph_data = process_line_graph_data(RANGE_OF_DAYS, data)

    # Get bar graph data
    bar_graph_data = process_bar_graph_data(data)

    # Get arb stats
    arb_stats = process_arb_stats(RANGE_OF_DAYS, data)

    # Send data to template
    context = {
        'current_exchanges': data['current_exchanges'], 
        'line_graph_data': line_graph_data,
        'bar_graph_data': bar_graph_data,
        'arb_stats': arb_stats,
    }

    return render(request, 'spread/index.html', context)

def get_database_data(range_of_days):
    """Retrieve all required data from database."""
    data = {}

    # Get queryset of all exchanges - parse into list.
    data['current_exchanges'] = []
    data['exchanges_queryset'] = Price.objects.all().values("exchange").distinct()

    # If Django migration has not yet been run will return None.
    try:
        for exchange in data['exchanges_queryset']:
            data['current_exchanges'].append(exchange['exchange'])
    except OperationalError:
        return None

    # If no entries in database yet, return None.
    if not data['exchanges_queryset']:
        return None

    # Get data from DB, entire range of days for processing. 
    data['graph_raw_data'] = Price.objects.filter(date__gte=timezone.now()-timedelta(days=range_of_days))

    # Get the latest price of each exchange and place in a list.
    data['list_of_latest_prices'] = []
    for exchange in data['exchanges_queryset']:
        # Get latest entry of each exchange
        latest_price = Price.objects.filter(exchange=exchange['exchange']).latest('date')
        data['list_of_latest_prices'].append(latest_price)

    # Get the average price across the range of days for each exchange, append to a list.
    # [{'exchange': 'Luno', 'price': 154982.43624161073}, ]
    data['average_stats_list'] = []
    for exchange in data['exchanges_queryset']:
        exchange_raw_data = Price.objects.filter(exchange=exchange['exchange']).filter(date__gte=timezone.now()-timedelta(days=range_of_days))
        data['average_stats_list'].append({'exchange': exchange['exchange'], 'price': exchange_raw_data.aggregate(Avg('price'))['price__avg']})

    return data

def process_line_graph_data(range_of_days, data):
    """Process the data for plotting line graph."""
    line_graph_data = {}

    # Constants    
    TOTAL_HOURS = 24 * range_of_days
    MILLISECONDS = 1000

    # Functions to round up or down to nearest 10 000.
    def round_up_10000(n):
        return int(math.ceil(n / 10000.0)) * 10000

    def round_down_10000(n):
        return n - (n % 10000)

    # Create a time series of one hour intervals for specified range of days.
    base = datetime.today() - timedelta(days=range_of_days)
    date_list = [base + timedelta(hours=x) for x in range (0, TOTAL_HOURS)]

    # Create "template" data structure {hour_interval: {exchange: price}, {exchange: price}}
    # Use OrderedDict so that we can rely on order later on in template for graphing
    graph_data_template = OrderedDict()
    for interval in date_list:
        graph_data_template[interval] = OrderedDict()
        for exchange in data['current_exchanges']:
            graph_data_template[interval][exchange] = "null"

    # Populate our template. We don't care too much about accuracy its hour based entries. 
    # Keeps null price entry if no price for that time interval
    # {hour_interval: {exchange: price}, {exchange: price}} -> {hour_interval: {"Luno": 120000}, {Bitfinex: "null"}}
    for raw_entry in data['graph_raw_data']:
        for template_entry in graph_data_template:
            if raw_entry.date.strftime("%Y-%m-%d %H") == template_entry.strftime("%Y-%m-%d %H"):
                graph_data_template[template_entry][raw_entry.exchange] = raw_entry.price

    # Convert to Google Charts friendly data, list of strings essentially. Epoch time must be in milliseconds, 
    # {hour_interval: {"Luno": 120000}, {Bitfinex: "null"}} -> [new Date (1511651498000), 144498.00, null, 124025.82, 122723.97]
    line_graph_data['data_points'] = []
    for time, exchange_data in graph_data_template.items():
        chart_entry = []
        # Convert epoch time to epoch milliseconds + timezone offset for Google Charts.
        timezone_offset = settings.UTC_TIMEZONE_OFFSET_IN_SECONDS
        chart_entry.append("new Date (" + str((int(time.strftime("%s")) + timezone_offset) * MILLISECONDS) + ")")
        # Add each exchange data points price to list
        for exchange, price in exchange_data.items():
            chart_entry.append(str(price))
            line_graph_data['data_points'].append(chart_entry)

    # Get max and min values for graph range to nearest 10 000.
    line_graph_data['graph_max'] = round_up_10000(int(data['graph_raw_data'].aggregate(Max('price'))['price__max']))
    line_graph_data['graph_min'] = round_down_10000(int(data['graph_raw_data'].aggregate(Min('price'))['price__min']))

    # Get list of colours for graph, if less colours defined than exchanges, use black instead.
    line_graph_data['line_graph_colours'] = []
    try:
        if len(settings.LINE_COLOURS) < data['exchanges_queryset'].count():
            for i in range(0,exchanges_queryset.count()):
                line_graph_data['line_graph_colours'].append("000000")
        else:
            line_graph_data['line_graph_colours'] = settings.LINE_COLOURS[:data['exchanges_queryset'].count()]
    except KeyError: 
        for i in range(0,data['exchanges_queryset'].count()):
            line_graph_data['line_graph_colours'].append("000000")

    return line_graph_data

def process_bar_graph_data(data):
    """Process the data for plotting bar graph."""
    bar_graph_data = {}

    # Get list of colours for graph, if less colours defined than exchanges, use black instead.
    bar_graph_data['bar_graph_colours'] = []
    try:
        if len(settings.BAR_COLOURS) < data['exchanges_queryset'].count():
            for i in range(0,data['exchanges_queryset'].count()):
                bar_graph_data['bar_graph_colours'].append("000000")
        else:
            bar_graph_data['bar_graph_colours'] = settings.BAR_COLOURS[:data['exchanges_queryset'].count()]
    except KeyError:
        for i in range(0,data['exchanges_queryset'].count()):
            bar_graph_data['bar_graph_colours'].append("000000")

    # Build data for bar graph, format: ['Exchange', 'Volume', { role: 'style' }]
    bar_graph_data['data_points'] = []
    for exchange_entry, graph_colour in zip(data['list_of_latest_prices'], bar_graph_data['bar_graph_colours']):
        bar_graph_entry = []
        bar_graph_entry.append(exchange_entry.exchange)
        # Get latest 24 hour volume of exchange
        bar_graph_entry.append(int(exchange_entry.volume))
        bar_graph_entry.append(graph_colour)
        bar_graph_data['data_points'].append(bar_graph_entry)

    return bar_graph_data

def process_arb_stats(range_of_days, data):
    """Process the data for arbitrage stats."""
    arb_stats = {}

    # Get stats on arbitrage, latest max and min. Lambda function returns queryset.
    arb_stats['latest_max'] = max(data['list_of_latest_prices'], key=lambda x:x.price)
    arb_stats['latest_min'] = min(data['list_of_latest_prices'], key=lambda x:x.price)
    arb_stats['time'] = data['list_of_latest_prices'][0].date

    # Get stats on arbitrage, average max and min. Lambda function returns the dictionary above.
    arb_stats['average_max'] = max(data['average_stats_list'], key=lambda x:x['price'])
    arb_stats['average_min'] = min(data['average_stats_list'], key=lambda x:x['price'])

    return arb_stats
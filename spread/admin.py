from django.contrib import admin
from spread.models import Price
from spread.models import Exchange_rate

admin.site.register(Price)
admin.site.register(Exchange_rate)
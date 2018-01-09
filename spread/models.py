from django.db import models
from django.utils import timezone

class Price(models.Model):
    exchange = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    volume = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    currency = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = 'Prices'

    def __str__(self):
        return str(self.exchange) + ": R" + str(format(self.price, ',')) + " - " + str(self.date.strftime('%Y-%m-%d %H:%M'))

class Exchange_rate(models.Model):
    currency = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = 'Exchange Rate'

    def __str__(self):
        return str(self.currency) + " - " + str(format(self.price, ',')) + " - " + str(self.date.strftime('%Y-%m-%d %H:%M'))
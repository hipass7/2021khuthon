from django.conf import settings
from django.db import models


class TradingRecord(models.Model):
    avg_price = models.FloatField()
    executed_qty = models.FloatField()
    fee = models.FloatField()
    cum_quote = models.FloatField()
    side = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    type = models.CharField(max_length=20)
    symbol = models.CharField(max_length=20)
    trade_diff_rate = models.FloatField()
    target_price = models.FloatField()
    datetime = models.DateTimeField()



    def __str__(self):
        return f"{self.datetime} / {self.side} {self.avg_price}"


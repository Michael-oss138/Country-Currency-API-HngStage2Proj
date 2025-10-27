from django.db import models
from django.utils import timezone

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_lenght=200, unique=True)
    capital = models.CharField(maz_lenght=200, null=True, blank=True)
    region = models.CharField(max_lebght=200, null=True, blank=True)
    population = models.BigIntegerFIeld()
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    exchange_rate = models.DecimalField(max_length=10, decimal_places=4, null=True, blank=True)
    estimated_gdp = models.FLoatField(null=True, blank=True)
    flag_url = models.URLField(null=True, blank=True)
    last_refreshed_at = models.DateTImeField(default=timezone.now)

    def __str__(self):
        return self.name

class RefreshStatus(models.Model):
    last_refreshed_at = models.DateTImeField(default=timezone.now)

    
from django.db import models
from django.utils import timezone

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_lenght=200, unique=True)
    capital = models.CharField(maz_lenght=200, null=True, blank=True)
    region = models.CharField(max_lebght=200, null=True, blank=True)
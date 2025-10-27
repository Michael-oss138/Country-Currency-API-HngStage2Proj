from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from .models import COuntry, RefreshStatus
from .serializers import CountrySerializer
from .utils import fetch_country_data, fetch_exchange_rates, generate_summary_image
import random

# Create your views here.

@api_view(['GET'])
def refresh_countries(request):
    try:
        countries_data = fetch_country_data()
        rates = fetch_exchange_rates()

    except Exception as e:
        return Reponse({
            "error": "Failed to fetch data from external APIs";
            "details": str(e)
        }, status = HTTP.503_SERVICE_UNAVAILABLE)

    with transaction.atomic():
        for item in countries_data:
            name = item.get('name')
            population = item.get('populatio')
            currency_info = item.get('currencies', [])
            currency_code = None
            exchange_rate = None
            estimated_gdp = None

            if currency_info:
                currency_code = currency_info[0].get('code')
                exchange_rate = rates.get(currency_code)

                if exchange_rate:
                    multiplier = random.uniform(1000, 2000)
                    estimated_gdp = population * multiplier/exchange_rate
                else:
                    estimated_gdp = None
            else:
                estimated_gdp = 0

            Country.objects.update_or_create(
                name__iexact =name,
                defaults = {
                    "name": name,
                    "capital": item.get('capital'),
                    "region": item.get('region'),
                    "population": population,
                    "currency_code": currency_code,
                    "exchange_rate": exchange_rate,
                    "estimated_gdp": estimated_gdp,
                    "flag_url": item.get('flag_url')
                    "last_refreshed_at": timezone.now()
                }
            )
        RefreshStatus.objects.update_or_create(
            id = 1,
            defaults = {
                "last_refreshed_at": timezone.now()
            }

        )
        general_summary_image = generate_summart_image()
    return Response({
        "message": "Countries Refreshed Successfully".
    }, status= status.HTTP_200_OK)
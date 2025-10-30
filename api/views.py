from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from .models import Country, RefreshStatus
from .serializers import CountrySerializer
from .utils import fetch_country_data, fetch_exchange_rates, generate_summary_image
import random
import os


@api_view(['POST'])
def refresh_countries(request):
    try:
        countries_data = fetch_country_data()
    except Exception:
        return Response({
            "error": "External data source unavailable",
            "details": "Could not fetch data from restcountries API"
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        rates = fetch_exchange_rates()
    except Exception:
        return Response({
            "error": "External data source unavailable",
            "details": "Could not fetch data from exchange rate API"
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    with transaction.atomic():
        for item in countries_data:
            name = item.get('name')
            population = item.get('population', 0)
            capital = item.get('capital')
            region = item.get('region')
            flag = item.get('flag')
            currencies = item.get('currencies', [])

            # Default values
            currency_code = None
            exchange_rate = None
            estimated_gdp = 0

            if currencies:
                currency_code = currencies[0].get('code')
                exchange_rate = rates.get(currency_code)
                if exchange_rate:
                    multiplier = random.uniform(1000, 2000)
                    estimated_gdp = (population * multiplier) / exchange_rate
                else:
                    estimated_gdp = 0
            else:
                estimated_gdp = 0

            existing_country = Country.objects.filter(name__iexact=name).first()
            if existing_country:
                # Update existing record
                existing_country.capital = capital
                existing_country.region = region
                existing_country.population = population
                existing_country.currency_code = currency_code
                existing_country.exchange_rate = exchange_rate
                existing_country.estimated_gdp = estimated_gdp
                existing_country.flag_url = flag
                existing_country.last_refreshed_at = timezone.now()
                existing_country.save()
            else:
                # Create new record
                Country.objects.create(
                    name=name,
                    capital=capital,
                    region=region,
                    population=population,
                    currency_code=currency_code,
                    exchange_rate=exchange_rate,
                    estimated_gdp=estimated_gdp,
                    flag_url=flag,
                    last_refreshed_at=timezone.now()
                )

        RefreshStatus.objects.update_or_create(
            id=1,
            defaults={'last_refreshed_at': timezone.now()}
        )

        generate_summary_image()

    return Response({"message": "Countries refreshed successfully"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_all_countries(request):
    region = request.GET.get('region')
    currency = request.GET.get('currency')
    sort = request.GET.get('sort')

    countries = Country.objects.all()

    if region:
        countries = countries.filter(region__iexact=region)
    if currency:
        countries = countries.filter(currency_code__iexact=currency)

    if sort == 'gdp_desc':
        countries = countries.order_by('-estimated_gdp')
    elif sort == 'gdp_asc':
        countries = countries.order_by('estimated_gdp')

    serializer = CountrySerializer(countries, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_country(request, name):
    country = get_object_or_404(Country, name__iexact=name)
    serializer = CountrySerializer(country)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_country(request, name):
    country = get_object_or_404(Country, name__iexact=name)
    country.delete()
    return Response({"message": f"{name} deleted successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_status(request):
    total = Country.objects.count()
    refresh_status = RefreshStatus.objects.first()
    return Response({
        "total_countries": total,
        "last_refreshed_at": refresh_status.last_refreshed_at if refresh_status else None
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_summary_image(request):
    image_path = "cache/summary.png"
    if not os.path.exists(image_path):
        return Response({"error": "Summary image not found"}, status=status.HTTP_404_NOT_FOUND)
    return FileResponse(open(image_path, 'rb'), content_type='image/png')

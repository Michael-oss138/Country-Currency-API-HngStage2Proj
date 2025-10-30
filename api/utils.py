import requests
import os
from PIL import Image, ImageDraw, ImageFont
from django.utils import timezone
from .models import Country, RefreshStatus


def fetch_country_data():
    url = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def fetch_exchange_rates():
    url = "https://open.er-api.com/v6/latest/USD"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json().get('rates', {})


def generate_summary_image():
    os.makedirs("cache", exist_ok=True)
    countries = Country.objects.all().order_by('-estimated_gdp')[:5]
    total = Country.objects.count()
    status = RefreshStatus.objects.first()

    img = Image.new('RGB', (600, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.text((20, 20), f"Total Countries: {total}", fill=(0, 0, 0), font=font)
    if status:
        draw.text((20, 50), f"Last Refreshed: {status.last_refreshed_at.strftime('%Y-%m-%d %H:%M:%S')}", fill=(0, 0, 0), font=font)
    draw.text((20, 90), "Top 5 by Estimated GDP:", fill=(0, 0, 0), font=font)

    y = 120
    for country in countries:
        text = f"{country.name} - {round(country.estimated_gdp or 0, 2):,}"
        draw.text((40, y), text, fill=(0, 0, 0), font=font)
        y += 25

    img.save("cache/summary.png")

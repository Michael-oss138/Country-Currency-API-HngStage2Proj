import requests
from PIL import Image, ImageDraw, ImageFont
from django.utils import timezone
from .models import Country, RefreshStatus
from io import BytesIO
import os

COUNTRIES_URL = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
RATES_URL = "https://open.er-api.com/v6/latest/USD"

def fetch_country_data():
    resp = requests.get(COUNTRIES_URL, timeout=10)
    if resp.status_code != 200:
        raise Exception("Could not fetch data from restcountries API")
    return resp.json()

def fetch_exchange_rates():
    resp = requests.get(RATES_URL, timeout=10)
    if resp.status_code != 200:
        raise Exception("Could not fetch data from exchange API")
    return resp.json().get("rates", {})

def generate_summary_image():
    total = Country.objects.count()
    top5 = Country.objects.order_by('-estimated_gdp')[:5]
    last_refresh = RefreshStatus.objects.first().last_refreshed_at

    img = Image.new('RGB', (600, 400), color='white')
    d = ImageDraw.Draw(img)

    y = 40
    d.text((20, y), f"Total Countries: {total}", fill="black"); y += 40
    d.text((20, y), "Top 5 by Estimated GDP:", fill="black"); y += 30

    for c in top5:
        d.text((40, y), f"{c.name}: {round(c.estimated_gdp or 0, 2)}", fill="black")
        y += 25

    d.text((20, y+20), f"Last Refresh: {last_refresh.strftime('%Y-%m-%d %H:%M:%S')}", fill="gray")

    os.makedirs("cache", exist_ok=True)
    img.save("cache/summary.png")
# countries/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('countries/refresh', views.refresh_countries),
    path('countries', views.get_all_countries),
    path('countries/<str:name>', views.get_country),
    path('countries/image', views.get_summary_image),
    path('status', views.get_status),
]

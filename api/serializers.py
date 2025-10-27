from rest_framework import serializers
from .models import Country

class CountrySerializer(serializers.Serializer):
    class Meta:
        models = Country
        fields = '__all__'
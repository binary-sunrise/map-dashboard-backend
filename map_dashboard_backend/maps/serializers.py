from rest_framework import serializers
from .models import Location
from django.contrib.gis.geos import Point

class LocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'description', 'point', 'latitude', 'longitude']
        read_only_fields = ['point']
    
    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        point = Point(longitude, latitude)
        location = Location.objects.create(point=point, **validated_data)
        return location
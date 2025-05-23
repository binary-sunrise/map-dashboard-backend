from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Location
from django.contrib.gis.geos import Point

class LocationSerializer(GeoFeatureModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    
    class Meta:
        model = Location
        geo_field = "point"
        fields = ['id', 'name', 'description', 'latitude', 'longitude']
    
    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        point = Point(longitude, latitude)
        location = Location.objects.create(point=point, **validated_data)
        return location
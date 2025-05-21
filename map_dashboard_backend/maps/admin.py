from django.contrib import admin
from django.contrib.gis import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.GISModelAdmin):
    list_display = ('name', 'point')
    default_lon = -1000000  # Default map center
    default_lat = 4500000
    default_zoom = 4
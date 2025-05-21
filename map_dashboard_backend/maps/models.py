# map_dashboard_backend/maps/models.py
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    point = models.PointField(geography=True, srid=4326)  # WGS84
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
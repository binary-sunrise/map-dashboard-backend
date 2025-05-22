# map_dashboard_backend/maps/models.py
from django.contrib.gis.db import models as gis_models
from django.db import models

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    point = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    linestring = gis_models.LineStringField(geography=True, srid=4326, null=True, blank=True)
    polygon = gis_models.PolygonField(geography=True, srid=4326, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
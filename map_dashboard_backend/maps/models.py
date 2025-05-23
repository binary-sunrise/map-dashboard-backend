from django.contrib.gis.db import models as gis_models
from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    point = gis_models.PointField(geography=True, srid=4326)  # Removed null=True, blank=True
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
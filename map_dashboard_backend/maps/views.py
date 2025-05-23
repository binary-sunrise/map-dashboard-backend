
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Location
from .serializers import LocationSerializer
from django.contrib.gis.geos import Point, GEOSGeometry
from django.contrib.gis.db.models.functions import Distance as DistanceFunc
from django.contrib.gis.geos import GEOSException
import json

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by distance from point if lat/lng provided
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        distance = self.request.query_params.get('distance', 10000)  # default 10km
        
        if lat and lng:
            point = Point(float(lng), float(lat))
            queryset = queryset.filter(point__distance_lte=(point, Distance(m=distance)))
        
        return queryset


class LocationBBoxFilterView(viewsets.ReadOnlyModelViewSet):
    """
    Filter locations within a bounding box (minx, miny, maxx, maxy)
    Example: /api/locations/bbox/?bbox=-180,-90,180,90
    """
    serializer_class = LocationSerializer
    
    def get_queryset(self):
        queryset = Location.objects.all()
        bbox = self.request.query_params.get('bbox')
        if bbox:
            try:
                minx, miny, maxx, maxy = map(float, bbox.split(','))
                queryset = queryset.filter(
                    point__bboverlaps=(minx, miny, maxx, maxy)
                )
            except (ValueError, TypeError):
                pass
        return queryset


class NearestLocationsView(viewsets.ReadOnlyModelViewSet):
    """
    Find nearest locations to a point (k-nearest neighbors)
    Example: /api/locations/nearest/?lat=40.7128&lng=-74.0060&limit=5
    """
    serializer_class = LocationSerializer
    
    def get_queryset(self):
        queryset = Location.objects.all()
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        limit = int(self.request.query_params.get('limit', 5))
        
        if lat and lng:
            point = Point(float(lng), float(lat), srid=4326)
            queryset = queryset.filter(point__isnull=False).annotate(
                distance=DistanceFunc('point', point)
            ).order_by('distance')[:limit]
        
        return queryset

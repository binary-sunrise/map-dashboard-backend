from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Location
from .serializers import LocationSerializer
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

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
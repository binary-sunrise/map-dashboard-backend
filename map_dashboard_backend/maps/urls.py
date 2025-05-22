from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (LocationViewSet,LocationBBoxFilterView,  LocationIntersectionView,NearestLocationsView)

router = DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'locations-bbox', LocationBBoxFilterView, basename='locations-bbox')
router.register(r'locations-intersects', LocationIntersectionView, basename='locations-intersects')
router.register(r'locations-nearest', NearestLocationsView, basename='locations-nearest')

urlpatterns = [
    path('', include(router.urls)),
    
]


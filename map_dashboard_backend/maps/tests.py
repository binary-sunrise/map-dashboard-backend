# maps/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.gis.geos import Point
from .models import Location

class LocationModelTest(TestCase):

    def test_create_location(self):
        location = Location.objects.create(
            name='Test Location',
            description='Testing location description',
            point=Point(100, 50),
        )

        self.assertEqual(location.name, 'Test Location')
        self.assertEqual(location.description, 'Testing location description')
        self.assertTrue(location.point == Point(100, 50, srid=4326))

class LocationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.create_location_url = reverse('location-list')
        self.location = Location.objects.create(
            name='Test Location for API',
            description='Testing description for API',
            point=Point(-74.0, 40.71)
        )

    def test_get_locations_list(self):
        response = self.client.get(self.create_location_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_location_detail(self):
        detail_url = reverse('location-detail', args=[str(self.location.id)])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Location for API')

    def test_filter_by_distance(self):
        filtered_url = self.create_location_url + "?lat=40.71&lng=-74.0&distance=10000"
        response = self.client.get(filtered_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_search_locations(self):
        search_url = self.create_location_url + "?search=Test"
        response = self.client.get(search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_ordering_locations(self):
        order_url = self.create_location_url + "?ordering=name"
        response = self.client.get(order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_404_on_invalid_id(self):
        invalid_url = reverse('location-detail', args=['123e4567-e89b-12d3-a456-426614174000'])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
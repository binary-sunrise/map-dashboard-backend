# maps/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.gis.geos import Point
from .models import Location
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

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

class LocationAPITest(APITestCase): # Changed from TestCase to APITestCase
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword')
        cls.token = Token.objects.create(user=cls.user)
        
        cls.location = Location.objects.create(
            name='Test Location for API',
            description='Testing description for API',
            point=Point(-74.0, 40.71) # Longitude, Latitude
        )
        cls.list_create_url = reverse('location-list')
        cls.detail_url = reverse('location-detail', args=[str(cls.location.id)])

    def setUp(self):
        # APIClient is automatically available in APITestCase as self.client
        pass

    # Renamed for clarity and to ensure it's for unauthenticated access
    def test_list_locations_unauthenticated(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response is a list (or a paginated list which has 'results')
        if 'results' in response.data:
            self.assertIsInstance(response.data['results'], list)
        else:
            self.assertIsInstance(response.data, list)


    # Renamed for clarity and to ensure it's for unauthenticated access
    def test_retrieve_location_unauthenticated(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming GeoJSON structure from GeoFeatureModelSerializer
        self.assertEqual(response.data['type'], 'Feature')
        self.assertIn('geometry', response.data)
        self.assertIn('properties', response.data)
        self.assertEqual(response.data['properties']['name'], 'Test Location for API')

    def test_geojson_output_structure_and_content_type(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check Content-Type, DRF-GIS typically uses application/vnd.geo+json
        # If this fails, it might be application/json, adjust as needed.
        self.assertEqual(response.accepted_media_type, 'application/vnd.geo+json')
        
        # Assert GeoJSON structure
        self.assertEqual(response.data['type'], 'Feature')
        self.assertIsNotNone(response.data['id']) # GeoFeatureModelSerializer includes id at top level
        self.assertIn('geometry', response.data)
        self.assertEqual(response.data['geometry']['type'], 'Point')
        # Coordinates are [longitude, latitude]
        self.assertEqual(response.data['geometry']['coordinates'], [-74.0, 40.71])
        
        self.assertIn('properties', response.data)
        self.assertEqual(response.data['properties']['name'], 'Test Location for API')
        self.assertEqual(response.data['properties']['description'], 'Testing description for API')
        # The 'point' field itself is usually not in properties as it's the geometry
        self.assertNotIn('point', response.data['properties'])


    def test_filter_by_distance(self): # Kept existing test
        # Note: This test might need adjustment if GeoJSON output is paginated differently
        filtered_url = self.list_create_url + "?lat=40.71&lng=-74.0&distance=10000"
        response = self.client.get(filtered_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data: # Handle paginated or non-paginated response
            self.assertGreater(len(response.data['results']), 0)
        else:
            self.assertGreater(len(response.data), 0)


    def test_search_locations(self): # Kept existing test
        search_url = self.list_create_url + "?search=Test"
        response = self.client.get(search_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            self.assertGreater(len(response.data['results']), 0)
        else:
            self.assertGreater(len(response.data), 0)
    
    def test_ordering_locations(self): # Kept existing test
        order_url = self.list_create_url + "?ordering=name"
        response = self.client.get(order_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            self.assertGreater(len(response.data['results']), 0)
        else:
            self.assertGreater(len(response.data), 0)

    def test_404_on_invalid_id(self): # Kept existing test
        invalid_url = reverse('location-detail', args=['123e4567-e89b-12d3-a456-426614174000'])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Authentication and Permission Tests ---

    def test_create_location_unauthenticated(self):
        data = {'name': 'New Location', 'description': 'Unauth create', 'latitude': 40.0, 'longitude': -74.0}
        response = self.client.post(self.list_create_url, data)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_create_location_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {'name': 'New Auth Location', 'description': 'Auth create', 'latitude': 41.0, 'longitude': -73.0}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['properties']['name'], 'New Auth Location')
        # Check if 'id' is present in the response properties or at the top level
        self.assertTrue('id' in response.data or 'id' in response.data['properties'])


    def test_update_location_unauthenticated(self):
        data = {'name': 'Updated Name Unauth', 'description': 'Updated desc', 'latitude': self.location.point.y, 'longitude': self.location.point.x}
        # PUT
        response_put = self.client.put(self.detail_url, data)
        self.assertIn(response_put.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        # PATCH
        response_patch = self.client.patch(self.detail_url, {'name': 'Partial Update Unauth'})
        self.assertIn(response_patch.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_update_location_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        # PUT
        put_data = {
            'name': 'Updated Name Auth PUT', 
            'description': 'Updated desc Auth PUT', 
            'latitude': 40.72, # New latitude
            'longitude': -74.01 # New longitude
        }
        response_put = self.client.put(self.detail_url, put_data, format='json')
        self.assertEqual(response_put.status_code, status.HTTP_200_OK)
        self.assertEqual(response_put.data['properties']['name'], 'Updated Name Auth PUT')
        # Verify the geometry was updated
        self.assertAlmostEqual(response_put.data['geometry']['coordinates'][0], -74.01, places=5)
        self.assertAlmostEqual(response_put.data['geometry']['coordinates'][1], 40.72, places=5)


        # PATCH
        patch_data = {'description': 'Partial Update Auth PATCH'}
        response_patch = self.client.patch(self.detail_url, patch_data, format='json')
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(response_patch.data['properties']['description'], 'Partial Update Auth PATCH')
        # Ensure name from PUT is still there
        self.assertEqual(response_patch.data['properties']['name'], 'Updated Name Auth PUT')


    def test_delete_location_unauthenticated(self):
        response = self.client.delete(self.detail_url)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_delete_location_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        # Create a new location to delete for this specific test
        temp_location = Location.objects.create(name="To Be Deleted", description="Temp", point=Point(1,1))
        temp_detail_url = reverse('location-detail', args=[str(temp_location.id)])
        
        response = self.client.delete(temp_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify it's actually deleted
        response_get = self.client.get(temp_detail_url)
        self.assertEqual(response_get.status_code, status.HTTP_404_NOT_FOUND)
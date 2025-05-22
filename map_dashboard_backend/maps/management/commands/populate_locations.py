from django.contrib.gis.geos import Point, LineString, Polygon
from django.core.management.base import BaseCommand
from faker import Faker
import random
from maps.models import Location

class Command(BaseCommand):
    help = "Populates the database with fake location data."

    def handle(self, *args, **kwargs):
        fake = Faker()
        for i in range(100):  # Create 100 random locations
            name = fake.company()
            description = fake.text(max_nb_chars=200)
            
            # Randomly decide which geometry type to use for this location
            geometry_type = random.choice(['point', 'linestring', 'polygon'])
            
            try:
                if geometry_type == 'point':
                    latitude = float(fake.latitude())
                    longitude = float(fake.longitude())
                    point = Point((longitude, latitude), srid=4326)
                    Location.objects.create(name=name, description=description, point=point)
                
                elif geometry_type == 'linestring':
                    num_points = random.randint(2, 5)
                    coords = [(float(fake.longitude()), float(fake.latitude())) for _ in range(num_points)]
                    linestring = LineString(coords, srid=4326)
                    Location.objects.create(name=name, description=description, linestring=linestring)
                
                elif geometry_type == 'polygon':
                    num_points = random.randint(4, 7)
                    coords = [(float(fake.longitude()), float(fake.latitude())) for _ in range(num_points - 1)]
                    coords.append(coords[0])  # Close the polygon
                    polygon = Polygon(coords, srid=4326)
                    if not polygon.valid:
                        polygon = polygon.buffer(0)
                    Location.objects.create(name=name, description=description, polygon=polygon)
                
                self.stdout.write(self.style.SUCCESS(f'Successfully created location {i+1} with type {geometry_type}.'))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating location {i+1}: {str(e)}'))
                continue
        
        self.stdout.write(self.style.SUCCESS('Successfully populated location data.'))
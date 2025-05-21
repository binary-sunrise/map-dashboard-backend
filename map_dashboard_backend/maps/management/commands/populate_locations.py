# map_dashboard_backend/maps/management/commands/populate_locations.py
from django.core.management.base import BaseCommand
from maps.models import Location
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from datetime import timezone
import random
from faker import Faker

class Command(BaseCommand):
    help = 'Populate database with sample geospatial data'

    def add_arguments(self, parser):
        parser.add_argument(
            'count',
            type=int,
            nargs='?',
            default=20,
            help='Number of locations to create (max 100)'
        )

    def handle(self, *args, **kwargs):
        fake = Faker()
        count = min(kwargs['count'], 100)  # Safety limit
        created = 0
        
        # Approximate coordinates for major world cities
        cities = {
            'New York': (-74.0060, 40.7128),
            'London': (-0.1278, 51.5074),
            '东京': (139.6917, 35.6895),
            'Paris': (2.3522, 48.8566),
            'Sydney': (151.2093, -33.8650),
        }
        
        # Create city-center locations
        for name, (lon, lat) in cities.items():
            try:
                Location.objects.create(
                    name=f"{name} HQ",
                    description=f"{name} corporate office",
                    point=Point(lon, lat)
                )
                self.stdout.write(self.style.SUCCESS(f'Created {name} HQ'))
                created += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Skipped {name}: {str(e)}'))

        # Create random locations
        for i in range(count):
            city = random.choice(list(cities.keys()))
            base_lon, base_lat = cities[city]
            
            try:
                location = Location.objects.create(
                    name=f"{city} restaurant {i+1}",
                    description=fake.sentence(),
                    point=Point(
                        base_lon + random.uniform(-0.5, 0.5),  # Create clusters around cities
                        base_lat + random.uniform(-0.5, 0.5)
                    )
                )
                created += 1
                if i % 5 == 0:
                    self.stdout.write(f'Created {i+1}/{count} locations...')
            except Exception as e:
                continue
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created} locations'))
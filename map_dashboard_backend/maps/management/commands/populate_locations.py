from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from faker import Faker
from maps.models import Location

class Command(BaseCommand):
    help = "Populates the database with fake location data."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing locations before populating',
        )

    def handle(self, *args, **options):
        fake = Faker()
        
        if options['clear']:
            self.stdout.write("Clearing existing locations...")
            Location.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing data cleared."))
        
        num_locations = 100
        created_count = 0
        
        for i in range(num_locations):
            try:
                name = fake.company()
                description = fake.text(max_nb_chars=200)
                latitude = float(fake.latitude())
                longitude = float(fake.longitude())
                point = Point(longitude, latitude, srid=4326)
                
                Location.objects.create(
                    name=name,
                    description=description,
                    point=point
                )
                created_count += 1
                self.stdout.write(f"Created location {i+1}: {name}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating location {i+1}: {str(e)}"))
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f"Created {created_count}/{num_locations} locations.")
        )
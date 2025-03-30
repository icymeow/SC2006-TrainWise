import csv
from django.core.management.base import BaseCommand
from activities.models import Activity

class Command(BaseCommand):
    help = 'Load activities data from CSV file'

    def handle(self, *args, **kwargs):
        # Clear existing activities
        Activity.objects.all().delete()
        
        # Path to your CSV file
        csv_file = 'data/Cleaned_Activities_Data.csv'
        
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Map intensity levels
                intensity_map = {
                    'Low': 'LOW',
                    'Medium': 'MEDIUM',
                    'High': 'HIGH'
                }
                
                # Map activity types
                activity_type_map = {
                    'Gym': 'GYM',
                    'Swimming': 'SWIMMING',
                    'Tennis': 'TENNIS',
                    'Basketball': 'BASKETBALL',
                    'Football': 'FOOTBALL',
                    'Running': 'RUNNING',
                    'Yoga': 'YOGA',
                    'Other': 'OTHER'
                }
                
                Activity.objects.create(
                    facility_name=row['Facility_Name'],
                    activity_type=activity_type_map.get(row['Activity_Type'], 'OTHER'),
                    description=row['Description'],
                    address=row['Address'],
                    latitude=float(row['Latitude']) if row['Latitude'] else None,
                    longitude=float(row['Longitude']) if row['Longitude'] else None,
                    intensity=intensity_map.get(row['Intensity'], 'MEDIUM'),
                    operating_hours=row['Operating_Hours'],
                    price_range=row['Price_Range'],
                    contact_info=row['Contact_Info'],
                    image_url=row.get('Image_URL', '')
                )
                
        self.stdout.write(self.style.SUCCESS('Successfully loaded activities data')) 
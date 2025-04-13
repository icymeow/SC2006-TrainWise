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
                # Split the activities string into a list
                activities_list = row['activities'].split('/')
                
                # For each activity in the facility, create a separate entry
                for activity in activities_list:
                    # Map activity types
                    activity_type_map = {
                        'Gym': 'GYM',
                        'Swimming': 'SWIMMING',
                        'Tennis': 'TENNIS',
                        'Basketball': 'BASKETBALL',
                        'Soccer': 'FOOTBALL',  # Map Soccer to Football
                        'Running': 'RUNNING',
                        'Jogging': 'RUNNING',  # Map Jogging to Running
                        'Walking': 'RUNNING',  # Map Walking to Running
                        'Badminton': 'BADMINTON',
                        'Table Tennis': 'TABLE_TENNIS',
                        'Volleyball': 'VOLLEYBALL',
                        'Squash': 'SQUASH',
                        'Hockey': 'HOCKEY',
                        'Pickleball': 'PICKLEBALL',
                        'Netball': 'NETBALL',
                        'Lawn Bowl': 'LAWN_BOWL'
                    }
                    
                    # Determine if indoor or outdoor based on Activity Type column
                    is_indoor = row['Activity Type'] == 'Indoor'
                    
                    # Create activity entry
                    Activity.objects.create(
                        facility_name=row['Facility Name'],
                        activity_type=activity_type_map.get(activity.strip(), 'OTHER'),
                        description=f"{activity.strip()} at {row['Facility Name']}",
                        address=row['Sports'],  # Using Sports field as location description
                        latitude=float(row['Latitude']) if row['Latitude'] else None,
                        longitude=float(row['Longitude']) if row['Longitude'] else None,
                        intensity='MEDIUM',  # Default intensity
                        operating_hours='9:00 AM - 10:00 PM',  # Default operating hours
                        price_range='$1.80 - $9.00',  # Updated default price range
                        contact_info='85993729',  # Updated default contact info
                        image_url='',  # No image URL in CSV
                        is_indoor=is_indoor
                    )
                
        self.stdout.write(self.style.SUCCESS('Successfully loaded activities data')) 
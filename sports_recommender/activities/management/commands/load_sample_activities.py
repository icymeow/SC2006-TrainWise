from django.core.management.base import BaseCommand
from activities.models import Activity

class Command(BaseCommand):
    help = 'Loads sample activities into the database'

    def handle(self, *args, **kwargs):
        # Sample activities data
        activities = [
            {
                'facility_name': 'ActiveSG Swimming Complex',
                'activity_type': 'SWIMMING',
                'description': 'Public swimming complex with multiple pools including a competition pool and a wading pool.',
                'intensity': 'MEDIUM',
                'is_indoor': False,
                'image_url': 'https://example.com/swimming.jpg',
                'address': '1 Stadium Place, Singapore 397628',
                'latitude': 1.3028,
                'longitude': 103.8744,
                'operating_hours': '6:30 AM - 9:30 PM',
                'price_range': '$2.50 - $4.00',
                'contact_info': '+65 6345 7111'
            },
            {
                'facility_name': 'Fitness First Gym',
                'activity_type': 'GYM',
                'description': 'Full-service gym with modern equipment and personal trainers available.',
                'intensity': 'HIGH',
                'is_indoor': True,
                'image_url': 'https://example.com/gym.jpg',
                'address': '68 Orchard Road, Singapore 238839',
                'latitude': 1.2988,
                'longitude': 103.8445,
                'operating_hours': '24/7',
                'price_range': '$89.00/month',
                'contact_info': '+65 6733 3777'
            },
            {
                'facility_name': 'East Coast Park Running Track',
                'activity_type': 'RUNNING',
                'description': 'Scenic running track along the East Coast Park with beautiful sea views.',
                'intensity': 'MEDIUM',
                'is_indoor': False,
                'image_url': 'https://example.com/running.jpg',
                'address': 'East Coast Park Service Road, Singapore 449876',
                'latitude': 1.3028,
                'longitude': 103.9122,
                'operating_hours': '24/7',
                'price_range': 'Free',
                'contact_info': 'N/A'
            },
            {
                'facility_name': 'Yoga Movement',
                'activity_type': 'YOGA',
                'description': 'Modern yoga studio offering various yoga classes for all levels.',
                'intensity': 'LOW',
                'is_indoor': True,
                'image_url': 'https://example.com/yoga.jpg',
                'address': '71 Robinson Road, Singapore 068895',
                'latitude': 1.2817,
                'longitude': 103.8507,
                'operating_hours': '7:00 AM - 9:00 PM',
                'price_range': '$25.00/class',
                'contact_info': '+65 6789 0123'
            }
        ]

        # Create activities
        for activity_data in activities:
            Activity.objects.create(**activity_data)
            self.stdout.write(self.style.SUCCESS(f'Successfully created activity: {activity_data["facility_name"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully loaded all sample activities')) 
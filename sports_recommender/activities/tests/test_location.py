from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Activity
from ..services import calculate_distance
from decimal import Decimal
import math

class LocationTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test activities with different locations
        self.central_activity = Activity.objects.create(
            facility_name='Central Gym',
            activity_type='GYM',
            description='Gym in central area',
            intensity='HIGH',
            is_indoor=True,
            address='Central Address',
            latitude=Decimal('1.3521'),  # Central Singapore
            longitude=Decimal('103.8198'),
            operating_hours='24/7',
            price_range='$50/month',
            contact_info='12345678'
        )

        self.east_activity = Activity.objects.create(
            facility_name='East Coast Park',
            activity_type='RUNNING',
            description='Running track at East Coast',
            intensity='MEDIUM',
            is_indoor=False,
            address='East Coast Address',
            latitude=Decimal('1.3028'),  # East Coast Park
            longitude=Decimal('103.9122'),
            operating_hours='24/7',
            price_range='Free',
            contact_info='87654321'
        )

        self.west_activity = Activity.objects.create(
            facility_name='West Sports Hall',
            activity_type='GYM',
            description='Sports hall in west',
            intensity='MEDIUM',
            is_indoor=True,
            address='West Address',
            latitude=Decimal('1.3521'),  # West Singapore
            longitude=Decimal('103.7000'),
            operating_hours='6:00 AM - 10:00 PM',
            price_range='$30/month',
            contact_info='98765432'
        )

    def test_distance_calculation(self):
        """Test distance calculation between two points"""
        # Test distance between Central and East Coast
        distance = calculate_distance(
            1.3521, 103.8198,  # Central Singapore
            1.3028, 103.9122   # East Coast Park
        )
        self.assertAlmostEqual(distance, 11.5, delta=1.0)  # Approximately 11.5 km

        # Test distance between Central and West
        distance = calculate_distance(
            1.3521, 103.8198,  # Central Singapore
            1.3521, 103.7000   # West Singapore
        )
        self.assertAlmostEqual(distance, 13.0, delta=1.0)  # Approximately 13.0 km

    def test_nearby_activities(self):
        """Test finding activities within a certain distance"""
        # User location in Central Singapore
        user_lat = 1.3521
        user_lng = 103.8198
        max_distance = 5.0  # 5 km radius

        # Get activities within range
        activities = Activity.objects.all()
        nearby_activities = []
        for activity in activities:
            distance = calculate_distance(
                user_lat, user_lng,
                float(activity.latitude),
                float(activity.longitude)
            )
            if distance <= max_distance:
                nearby_activities.append(activity)

        # Central activity should be nearby
        self.assertIn(self.central_activity, nearby_activities)
        # East and West activities should be too far
        self.assertNotIn(self.east_activity, nearby_activities)
        self.assertNotIn(self.west_activity, nearby_activities)

    def test_location_validation(self):
        """Test validation of location coordinates"""
        # Test valid coordinates
        self.assertTrue(self.central_activity.latitude is not None)
        self.assertTrue(self.central_activity.longitude is not None)

        # Test invalid coordinates
        with self.assertRaises(Exception):
            Activity.objects.create(
                facility_name='Invalid Location',
                activity_type='GYM',
                description='Test',
                intensity='HIGH',
                is_indoor=True,
                address='Test Address',
                latitude=Decimal('200.0000'),  # Invalid latitude
                longitude=Decimal('103.8198'),
                operating_hours='24/7',
                price_range='$50/month',
                contact_info='12345678'
            )

    def test_location_sorting(self):
        """Test sorting activities by distance"""
        # User location in Central Singapore
        user_lat = 1.3521
        user_lng = 103.8198

        # Calculate distances for all activities
        activities_with_distance = []
        for activity in Activity.objects.all():
            distance = calculate_distance(
                user_lat, user_lng,
                float(activity.latitude),
                float(activity.longitude)
            )
            activities_with_distance.append((activity, distance))

        # Sort by distance
        activities_with_distance.sort(key=lambda x: x[1])
        sorted_activities = [activity for activity, _ in activities_with_distance]

        # Central activity should be first
        self.assertEqual(sorted_activities[0], self.central_activity)

    def test_location_boundaries(self):
        """Test activities at different location boundaries"""
        # Test activities at extreme coordinates
        boundary_activities = [
            {
                'name': 'North Activity',
                'lat': Decimal('1.4700'),  # Northernmost point
                'lng': Decimal('103.8198')
            },
            {
                'name': 'South Activity',
                'lat': Decimal('1.2000'),  # Southernmost point
                'lng': Decimal('103.8198')
            },
            {
                'name': 'East Activity',
                'lat': Decimal('1.3521'),
                'lng': Decimal('104.0000')  # Easternmost point
            },
            {
                'name': 'West Activity',
                'lat': Decimal('1.3521'),
                'lng': Decimal('103.6000')  # Westernmost point
            }
        ]

        for activity_data in boundary_activities:
            activity = Activity.objects.create(
                facility_name=activity_data['name'],
                activity_type='OTHER',
                description='Boundary test',
                intensity='MEDIUM',
                is_indoor=False,
                address='Test Address',
                latitude=activity_data['lat'],
                longitude=activity_data['lng'],
                operating_hours='24/7',
                price_range='Free',
                contact_info='12345678'
            )
            self.assertTrue(activity.latitude is not None)
            self.assertTrue(activity.longitude is not None)

    def test_location_clustering(self):
        """Test grouping activities by location clusters"""
        # Create activities in the same area
        cluster_activities = []
        base_lat = 1.3521
        base_lng = 103.8198

        for i in range(3):
            activity = Activity.objects.create(
                facility_name=f'Cluster Activity {i+1}',
                activity_type='GYM',
                description='Cluster test',
                intensity='MEDIUM',
                is_indoor=True,
                address='Test Address',
                latitude=Decimal(str(base_lat + i * 0.001)),  # Slightly offset
                longitude=Decimal(str(base_lng + i * 0.001)),  # Slightly offset
                operating_hours='24/7',
                price_range='$50/month',
                contact_info='12345678'
            )
            cluster_activities.append(activity)

        # All activities should be within 1km of each other
        for i in range(len(cluster_activities)):
            for j in range(i + 1, len(cluster_activities)):
                distance = calculate_distance(
                    float(cluster_activities[i].latitude),
                    float(cluster_activities[i].longitude),
                    float(cluster_activities[j].latitude),
                    float(cluster_activities[j].longitude)
                )
                self.assertLess(distance, 1.0)  # Less than 1km apart 
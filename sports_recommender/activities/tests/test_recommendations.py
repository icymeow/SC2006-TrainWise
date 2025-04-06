from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Activity, UserPreference, ActivityHistory
from ..services import get_recommended_activities
from decimal import Decimal
import datetime

class RecommendationTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create user preferences
        self.user_pref = UserPreference.objects.create(
            user=self.user,
            preferred_activity_types='RUNNING,GYM',
            max_distance=5.0,
            indoor_preference=False
        )

        # Create test activities
        self.running_activity = Activity.objects.create(
            facility_name='Running Track',
            activity_type='RUNNING',
            description='Outdoor running track',
            intensity='MEDIUM',
            is_indoor=False,
            address='Test Address',
            latitude=Decimal('1.3521'),
            longitude=Decimal('103.8198'),
            operating_hours='24/7',
            price_range='Free',
            contact_info='12345678'
        )

        self.gym_activity = Activity.objects.create(
            facility_name='Fitness Center',
            activity_type='GYM',
            description='Modern gym facility',
            intensity='HIGH',
            is_indoor=True,
            address='Gym Address',
            latitude=Decimal('1.3522'),
            longitude=Decimal('103.8199'),
            operating_hours='6:00 AM - 10:00 PM',
            price_range='$50/month',
            contact_info='87654321'
        )

        self.swimming_activity = Activity.objects.create(
            facility_name='Swimming Pool',
            activity_type='SWIMMING',
            description='Olympic size pool',
            intensity='MEDIUM',
            is_indoor=True,
            address='Pool Address',
            latitude=Decimal('1.3523'),
            longitude=Decimal('103.8200'),
            operating_hours='7:00 AM - 9:00 PM',
            price_range='$2.50/entry',
            contact_info='98765432'
        )

    def test_basic_recommendations(self):
        """Test basic recommendation based on user preferences"""
        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 28
        }

        recommendations = get_recommended_activities(
            self.user,
            user_location,
            weather_data
        )

        # Should recommend activities matching user preferences
        self.assertTrue(len(recommendations) > 0)
        recommended_types = [activity.activity_type for activity in recommendations]
        self.assertIn('RUNNING', recommended_types)
        self.assertIn('GYM', recommended_types)
        self.assertNotIn('SWIMMING', recommended_types)

    def test_weather_based_recommendations(self):
        """Test recommendations based on weather conditions"""
        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }

        # Test rainy weather
        rainy_weather = {
            'condition': 'rainy',
            'temperature': 25
        }
        rainy_recommendations = get_recommended_activities(
            self.user,
            user_location,
            rainy_weather
        )
        self.assertTrue(all(activity.is_indoor for activity in rainy_recommendations))

        # Test sunny weather
        sunny_weather = {
            'condition': 'sunny',
            'temperature': 30
        }
        sunny_recommendations = get_recommended_activities(
            self.user,
            user_location,
            sunny_weather
        )
        self.assertTrue(any(not activity.is_indoor for activity in sunny_recommendations))

    def test_distance_based_recommendations(self):
        """Test recommendations based on distance"""
        # User location far from activities
        far_location = {
            'latitude': 1.4000,
            'longitude': 103.9000
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 28
        }

        recommendations = get_recommended_activities(
            self.user,
            far_location,
            weather_data
        )
        self.assertEqual(len(recommendations), 0)  # No recommendations within max_distance

    def test_history_based_recommendations(self):
        """Test recommendations based on user's activity history"""
        # Add some activity history
        ActivityHistory.objects.create(
            user=self.user,
            activity=self.running_activity,
            date_completed=datetime.date.today() - datetime.timedelta(days=1),
            duration=datetime.timedelta(hours=1),
            rating=5
        )

        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 28
        }

        recommendations = get_recommended_activities(
            self.user,
            user_location,
            weather_data
        )

        # Running activity should be recommended due to positive history
        self.assertTrue(any(activity.id == self.running_activity.id for activity in recommendations))

    def test_intensity_based_recommendations(self):
        """Test recommendations based on activity intensity"""
        # Update user preferences to prefer high intensity
        self.user_pref.preferred_activity_types = 'GYM'
        self.user_pref.save()

        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 28
        }

        recommendations = get_recommended_activities(
            self.user,
            user_location,
            weather_data
        )

        # Should recommend high intensity activities
        self.assertTrue(all(activity.intensity == 'HIGH' for activity in recommendations))

    def test_empty_recommendations(self):
        """Test case when no activities match criteria"""
        # Update user preferences to non-existent activity type
        self.user_pref.preferred_activity_types = 'NONEXISTENT'
        self.user_pref.save()

        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 28
        }

        recommendations = get_recommended_activities(
            self.user,
            user_location,
            weather_data
        )

        self.assertEqual(len(recommendations), 0) 
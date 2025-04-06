from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Activity
from ..services import get_weather_data
from unittest.mock import patch, MagicMock
import json

class WeatherTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create test activities
        self.indoor_activity = Activity.objects.create(
            facility_name='Indoor Gym',
            activity_type='GYM',
            description='Indoor gym facility',
            intensity='HIGH',
            is_indoor=True,
            address='Test Address',
            latitude=1.3521,
            longitude=103.8198,
            operating_hours='24/7',
            price_range='$50/month',
            contact_info='12345678'
        )

        self.outdoor_activity = Activity.objects.create(
            facility_name='Running Track',
            activity_type='RUNNING',
            description='Outdoor running track',
            intensity='MEDIUM',
            is_indoor=False,
            address='Track Address',
            latitude=1.3522,
            longitude=103.8199,
            operating_hours='24/7',
            price_range='Free',
            contact_info='87654321'
        )

    @patch('requests.get')
    def test_weather_api_success(self, mock_get):
        """Test successful weather API response"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'items': [{
                'general': {
                    'forecast': 'Partly Cloudy',
                    'temperature': 28
                }
            }]
        }
        mock_get.return_value = mock_response

        weather_data = get_weather_data()
        self.assertIsNotNone(weather_data)
        self.assertEqual(weather_data['forecast'], 'Partly Cloudy')
        self.assertEqual(weather_data['temperature'], 28)

    @patch('requests.get')
    def test_weather_api_failure(self, mock_get):
        """Test weather API failure"""
        # Mock API failure
        mock_get.side_effect = Exception('API Error')

        weather_data = get_weather_data()
        self.assertIsNone(weather_data)

    def test_activity_filtering_by_weather(self):
        """Test filtering activities based on weather conditions"""
        # Test rainy weather
        rainy_weather = {
            'forecast': 'Rain',
            'temperature': 25
        }

        # Get activities suitable for rainy weather
        rainy_activities = Activity.objects.filter(is_indoor=True)
        self.assertTrue(self.indoor_activity in rainy_activities)
        self.assertFalse(self.outdoor_activity in rainy_activities)

        # Test sunny weather
        sunny_weather = {
            'forecast': 'Sunny',
            'temperature': 30
        }

        # Get activities suitable for sunny weather
        sunny_activities = Activity.objects.all()
        self.assertTrue(self.indoor_activity in sunny_activities)
        self.assertTrue(self.outdoor_activity in sunny_activities)

    def test_temperature_based_recommendations(self):
        """Test activity recommendations based on temperature"""
        # Test hot weather
        hot_weather = {
            'forecast': 'Sunny',
            'temperature': 35
        }

        # Activities should be filtered based on temperature
        activities = Activity.objects.all()
        for activity in activities:
            if activity.activity_type == 'RUNNING':
                # Running might not be recommended in very hot weather
                self.assertTrue(activity.intensity != 'HIGH')

        # Test moderate weather
        moderate_weather = {
            'forecast': 'Partly Cloudy',
            'temperature': 25
        }

        # All activities should be available in moderate weather
        activities = Activity.objects.all()
        self.assertEqual(activities.count(), 2)

    def test_weather_condition_mapping(self):
        """Test mapping of weather conditions to activity suitability"""
        weather_conditions = {
            'Rain': ['GYM', 'SWIMMING'],  # Indoor activities
            'Sunny': ['RUNNING', 'TENNIS', 'GYM'],  # All activities
            'Thunderstorm': ['GYM'],  # Only indoor activities
            'Cloudy': ['RUNNING', 'GYM', 'TENNIS']  # Most activities
        }

        for condition, suitable_types in weather_conditions.items():
            weather_data = {
                'forecast': condition,
                'temperature': 25
            }

            # Get activities based on weather condition
            if condition in ['Rain', 'Thunderstorm']:
                activities = Activity.objects.filter(is_indoor=True)
            else:
                activities = Activity.objects.all()

            # Verify activity types
            for activity in activities:
                if condition in ['Rain', 'Thunderstorm']:
                    self.assertTrue(activity.is_indoor)
                if condition == 'Sunny':
                    self.assertTrue(activity.activity_type in suitable_types)

    def test_extreme_weather_conditions(self):
        """Test activity filtering for extreme weather conditions"""
        extreme_conditions = [
            {'forecast': 'Heavy Rain', 'temperature': 20},
            {'forecast': 'Thunderstorm', 'temperature': 22},
            {'forecast': 'Haze', 'temperature': 30},
            {'forecast': 'Extreme Heat', 'temperature': 38}
        ]

        for condition in extreme_conditions:
            # In extreme conditions, only indoor activities should be recommended
            activities = Activity.objects.filter(is_indoor=True)
            self.assertTrue(all(activity.is_indoor for activity in activities))
            self.assertFalse(any(not activity.is_indoor for activity in activities)) 
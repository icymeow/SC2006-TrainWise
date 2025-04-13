from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Activity, UserPreference, ActivityHistory
from ..services import get_recommended_activities, calculate_distance_score
from decimal import Decimal
import datetime

class RecommendationTests(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create user preferences
        self.user_pref = UserPreference.objects.create(
            user=self.user,
            preferred_activity_types=['RUNNING', 'GYM'],
            max_distance=10.0,
            preferred_intensity='MEDIUM'
        )

        # Create test activities
        self.indoor_gym = Activity.objects.create(
            facility_name='Test Gym',
            description='GYM',
            is_indoor=True,
            latitude=1.3521,
            longitude=103.8198,
            intensity='HIGH'
        )

        self.outdoor_running = Activity.objects.create(
            facility_name='Running Track',
            description='RUNNING',
            is_indoor=False,
            latitude=1.3522,
            longitude=103.8199,
            intensity='MEDIUM'
        )

        self.far_activity = Activity.objects.create(
            facility_name='Far Away Gym',
            description='GYM',
            is_indoor=True,
            latitude=2.3521,  # Very far from test location
            longitude=104.8198,
            intensity='MEDIUM'
        )

    def test_basic_recommendation_flow(self):
        """Test basic recommendation functionality with good weather"""
        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 28,
            'humidity': 70
        }

        recommendations = get_recommended_activities(self.user, user_location, weather_data)
        self.assertTrue(len(recommendations) > 0)
        # First recommendation should be nearby and match preferences
        first_rec = recommendations[0][0]
        self.assertTrue(
            first_rec.facility_name in ['Test Gym', 'Running Track'],
            "First recommendation should be a nearby preferred activity"
        )

    def test_weather_based_filtering(self):
        """Test recommendations during bad weather"""
        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }
        weather_data = {
            'condition': 'rain',
            'temperature': 25,
            'humidity': 90
        }

        recommendations = get_recommended_activities(self.user, user_location, weather_data)
        
        # Indoor activities should be prioritized in rain
        if recommendations:
            first_rec = recommendations[0][0]
            self.assertTrue(
                first_rec.is_indoor,
                "First recommendation during rain should be indoor"
            )

    def test_distance_based_filtering(self):
        """Test distance-based recommendations"""
        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 28,
            'humidity': 70
        }

        recommendations = get_recommended_activities(self.user, user_location, weather_data)
        
        # Far activity should be at the bottom or not included
        rec_activities = [rec[0] for rec in recommendations]
        if self.far_activity in rec_activities:
            self.assertGreater(
                rec_activities.index(self.far_activity),
                rec_activities.index(self.indoor_gym),
                "Far activity should be ranked lower than nearby activities"
            )

    def test_no_user_preferences(self):
        """Test recommendations when user has no preferences"""
        # Delete user preferences
        self.user_pref.delete()

        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 28,
            'humidity': 70
        }

        recommendations = get_recommended_activities(self.user, user_location, weather_data)
        self.assertEqual(len(recommendations), 0, "Should return empty list when no preferences")

    def test_extreme_weather_conditions(self):
        """Test recommendations during extreme weather"""
        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 36,  # Very hot
            'humidity': 90
        }

        recommendations = get_recommended_activities(self.user, user_location, weather_data)
        
        if recommendations:
            first_rec = recommendations[0][0]
            self.assertTrue(
                first_rec.is_indoor or 'SWIMMING' in first_rec.description.upper(),
                "First recommendation during extreme heat should be indoor or swimming"
            )

    def test_invalid_location_data(self):
        """Test recommendations with invalid location data"""
        user_location = {
            'latitude': None,
            'longitude': None
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 28,
            'humidity': 70
        }

        recommendations = get_recommended_activities(self.user, user_location, weather_data)
        self.assertEqual(len(recommendations), 0, "Should return empty list with invalid location")

    def test_activity_history_influence(self):
        """Test how activity history influences recommendations"""
        # Add activity history with high rating
        ActivityHistory.objects.create(
            user=self.user,
            activity=self.indoor_gym,
            date_completed=datetime.date.today() - datetime.timedelta(days=1),
            rating=5
        )

        user_location = {
            'latitude': 1.3521,
            'longitude': 103.8198
        }
        weather_data = {
            'condition': 'sunny',
            'temperature': 28,
            'humidity': 70
        }

        recommendations = get_recommended_activities(self.user, user_location, weather_data)
        
        if recommendations:
            first_rec = recommendations[0][0]
            self.assertEqual(
                first_rec,
                self.indoor_gym,
                "Activity with positive history should be recommended first"
            )

    def test_distance_score_calculation(self):
        """Test the distance score calculation function"""
        self.assertEqual(calculate_distance_score(0.5), 5, "Distance <= 1km should score 5")
        self.assertEqual(calculate_distance_score(1.5), 4, "Distance 1-2km should score 4")
        self.assertEqual(calculate_distance_score(2.5), 3, "Distance 2-3km should score 3")
        self.assertEqual(calculate_distance_score(4.0), 2, "Distance 3-5km should score 2")
        self.assertEqual(calculate_distance_score(6.0), 0, "Distance >5km should score 0")

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
            activity=self.outdoor_running,
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
        self.assertTrue(any(activity.id == self.outdoor_running.id for activity in recommendations))

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
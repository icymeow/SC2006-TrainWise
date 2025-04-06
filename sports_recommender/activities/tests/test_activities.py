from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Activity, ActivityHistory, FavoriteActivity, UserPreference
from decimal import Decimal

class ActivityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.activity = Activity.objects.create(
            facility_name='Test Facility',
            activity_type='RUNNING',
            description='Test description',
            intensity='MEDIUM',
            is_indoor=False,
            address='Test Address',
            latitude=Decimal('1.3521'),
            longitude=Decimal('103.8198'),
            operating_hours='9:00 AM - 9:00 PM',
            price_range='Free',
            contact_info='12345678'
        )

    def test_activity_creation(self):
        """Test activity creation and validation"""
        self.assertEqual(self.activity.facility_name, 'Test Facility')
        self.assertEqual(self.activity.activity_type, 'RUNNING')
        self.assertEqual(self.activity.intensity, 'MEDIUM')
        self.assertFalse(self.activity.is_indoor)

    def test_activity_list_view(self):
        """Test activity list view"""
        response = self.client.get(reverse('activity_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Facility')

    def test_activity_detail_view(self):
        """Test activity detail view"""
        response = self.client.get(reverse('activity_detail', args=[self.activity.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Facility')
        self.assertContains(response, 'Test description')

    def test_activity_search(self):
        """Test activity search functionality"""
        response = self.client.get(reverse('activity_search'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Facility')

    def test_add_to_favorites(self):
        """Test adding activity to favorites"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_favorite', args=[self.activity.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(FavoriteActivity.objects.filter(user=self.user, activity=self.activity).exists())

    def test_remove_from_favorites(self):
        """Test removing activity from favorites"""
        self.client.login(username='testuser', password='testpass123')
        FavoriteActivity.objects.create(user=self.user, activity=self.activity)
        response = self.client.post(reverse('remove_favorite', args=[self.activity.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(FavoriteActivity.objects.filter(user=self.user, activity=self.activity).exists())

    def test_add_activity_history(self):
        """Test adding activity to workout history"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('add_history'), {
            'activity_id': self.activity.id,
            'date_completed': '2024-04-03',
            'duration': '01:30:00',
            'rating': 4,
            'notes': 'Great workout!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ActivityHistory.objects.filter(user=self.user, activity=self.activity).exists())

    def test_activity_filtering(self):
        """Test activity filtering by type and intensity"""
        # Create another activity
        Activity.objects.create(
            facility_name='Indoor Gym',
            activity_type='GYM',
            description='Gym description',
            intensity='HIGH',
            is_indoor=True,
            address='Gym Address',
            latitude=Decimal('1.3521'),
            longitude=Decimal('103.8198'),
            operating_hours='24/7',
            price_range='$50/month',
            contact_info='87654321'
        )

        # Test filtering by activity type
        response = self.client.get(reverse('activity_list'), {'activity_type': 'GYM'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Indoor Gym')
        self.assertNotContains(response, 'Test Facility')

        # Test filtering by intensity
        response = self.client.get(reverse('activity_list'), {'intensity': 'HIGH'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Indoor Gym')
        self.assertNotContains(response, 'Test Facility')

    def test_activity_distance_calculation(self):
        """Test distance calculation between user and activities"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('get_distances'), {
            'latitude': 1.3521,
            'longitude': 103.8198
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(self.activity.id), response.json()['distances'])

    def test_user_preferences(self):
        """Test user preferences for activity recommendations"""
        self.client.login(username='testuser', password='testpass123')
        UserPreference.objects.create(
            user=self.user,
            preferred_activity_types='RUNNING,GYM',
            max_distance=5.0,
            indoor_preference=False
        )

        response = self.client.get(reverse('get_recommendations'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('recommendations', response.json()) 
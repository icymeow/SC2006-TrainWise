from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Activity, ActivityHistory
from datetime import datetime, timedelta
from decimal import Decimal

class WorkoutHistoryTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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

    def test_add_workout_history(self):
        """Test adding a workout to history"""
        history_entry = ActivityHistory.objects.create(
            user=self.user,
            activity=self.running_activity,
            date_completed=datetime.now().date(),
            duration=timedelta(hours=1),
            rating=4,
            notes='Great run!'
        )

        self.assertEqual(history_entry.user, self.user)
        self.assertEqual(history_entry.activity, self.running_activity)
        self.assertEqual(history_entry.rating, 4)
        self.assertEqual(history_entry.notes, 'Great run!')

    def test_get_user_history(self):
        """Test retrieving user's workout history"""
        # Add multiple history entries
        ActivityHistory.objects.create(
            user=self.user,
            activity=self.running_activity,
            date_completed=datetime.now().date() - timedelta(days=1),
            duration=timedelta(hours=1),
            rating=4
        )

        ActivityHistory.objects.create(
            user=self.user,
            activity=self.gym_activity,
            date_completed=datetime.now().date(),
            duration=timedelta(hours=2),
            rating=5
        )

        # Get user's history
        history = ActivityHistory.objects.filter(user=self.user).order_by('-date_completed')
        self.assertEqual(history.count(), 2)
        self.assertEqual(history[0].activity, self.gym_activity)
        self.assertEqual(history[1].activity, self.running_activity)

    def test_history_ordering(self):
        """Test history entries are ordered by date"""
        dates = [
            datetime.now().date() - timedelta(days=2),
            datetime.now().date() - timedelta(days=1),
            datetime.now().date()
        ]

        for date in dates:
            ActivityHistory.objects.create(
                user=self.user,
                activity=self.running_activity,
                date_completed=date,
                duration=timedelta(hours=1),
                rating=4
            )

        history = ActivityHistory.objects.filter(user=self.user).order_by('-date_completed')
        self.assertEqual(history[0].date_completed, dates[2])
        self.assertEqual(history[1].date_completed, dates[1])
        self.assertEqual(history[2].date_completed, dates[0])

    def test_history_filtering(self):
        """Test filtering workout history"""
        # Add history entries for different activities
        ActivityHistory.objects.create(
            user=self.user,
            activity=self.running_activity,
            date_completed=datetime.now().date(),
            duration=timedelta(hours=1),
            rating=4
        )

        ActivityHistory.objects.create(
            user=self.user,
            activity=self.gym_activity,
            date_completed=datetime.now().date(),
            duration=timedelta(hours=2),
            rating=5
        )

        # Filter by activity type
        running_history = ActivityHistory.objects.filter(
            user=self.user,
            activity__activity_type='RUNNING'
        )
        self.assertEqual(running_history.count(), 1)
        self.assertEqual(running_history[0].activity, self.running_activity)

        # Filter by rating
        high_rated_history = ActivityHistory.objects.filter(
            user=self.user,
            rating__gte=5
        )
        self.assertEqual(high_rated_history.count(), 1)
        self.assertEqual(high_rated_history[0].activity, self.gym_activity)

    def test_history_duration_calculation(self):
        """Test workout duration calculations"""
        # Add history entries with different durations
        ActivityHistory.objects.create(
            user=self.user,
            activity=self.running_activity,
            date_completed=datetime.now().date(),
            duration=timedelta(hours=1, minutes=30),
            rating=4
        )

        ActivityHistory.objects.create(
            user=self.user,
            activity=self.gym_activity,
            date_completed=datetime.now().date(),
            duration=timedelta(hours=2),
            rating=5
        )

        # Calculate total workout time
        total_duration = sum(
            (entry.duration.total_seconds() for entry in ActivityHistory.objects.filter(user=self.user)),
            timedelta()
        )
        self.assertEqual(total_duration.total_seconds(), 3.5 * 3600)  # 3.5 hours

    def test_history_validation(self):
        """Test validation of history entries"""
        # Test invalid rating
        with self.assertRaises(Exception):
            ActivityHistory.objects.create(
                user=self.user,
                activity=self.running_activity,
                date_completed=datetime.now().date(),
                duration=timedelta(hours=1),
                rating=6  # Invalid rating (should be 1-5)
            )

        # Test future date
        with self.assertRaises(Exception):
            ActivityHistory.objects.create(
                user=self.user,
                activity=self.running_activity,
                date_completed=datetime.now().date() + timedelta(days=1),
                duration=timedelta(hours=1),
                rating=4
            )

    def test_history_statistics(self):
        """Test workout history statistics"""
        # Add multiple history entries
        for i in range(5):
            ActivityHistory.objects.create(
                user=self.user,
                activity=self.running_activity,
                date_completed=datetime.now().date() - timedelta(days=i),
                duration=timedelta(hours=1),
                rating=4
            )

        # Calculate statistics
        total_workouts = ActivityHistory.objects.filter(user=self.user).count()
        avg_rating = ActivityHistory.objects.filter(user=self.user).aggregate(avg_rating=models.Avg('rating'))
        total_duration = sum(
            (entry.duration.total_seconds() for entry in ActivityHistory.objects.filter(user=self.user)),
            timedelta()
        )

        self.assertEqual(total_workouts, 5)
        self.assertEqual(avg_rating['avg_rating'], 4.0)
        self.assertEqual(total_duration.total_seconds(), 5 * 3600)  # 5 hours

    def test_history_deletion(self):
        """Test deletion of history entries"""
        # Add a history entry
        history_entry = ActivityHistory.objects.create(
            user=self.user,
            activity=self.running_activity,
            date_completed=datetime.now().date(),
            duration=timedelta(hours=1),
            rating=4
        )

        # Delete the entry
        history_entry.delete()
        self.assertFalse(ActivityHistory.objects.filter(id=history_entry.id).exists()) 
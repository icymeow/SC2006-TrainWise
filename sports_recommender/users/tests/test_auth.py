from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from ..models import UserProfile

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.test_user = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

    def test_user_registration(self):
        """Test user registration functionality"""
        response = self.client.post(self.register_url, self.test_user)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful registration
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Test profile creation
        user = User.objects.get(username='testuser')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_user_login(self):
        """Test user login functionality"""
        # Create a user first
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful login

    def test_user_logout(self):
        """Test user logout functionality"""
        # Create and login a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Should redirect after logout

    def test_invalid_registration(self):
        """Test registration with invalid data"""
        # Test with mismatched passwords
        invalid_data = self.test_user.copy()
        invalid_data['password2'] = 'differentpass'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_duplicate_username(self):
        """Test registration with duplicate username"""
        # Create a user first
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        response = self.client.post(self.register_url, self.test_user)
        self.assertEqual(response.status_code, 200)  # Should stay on same page
        self.assertEqual(User.objects.filter(username='testuser').count(), 1)

    def test_password_validation(self):
        """Test password validation rules"""
        # Test with too short password
        invalid_data = self.test_user.copy()
        invalid_data['password1'] = 'short'
        invalid_data['password2'] = 'short'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_email_validation(self):
        """Test email validation"""
        # Test with invalid email
        invalid_data = self.test_user.copy()
        invalid_data['email'] = 'invalid-email'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_required_fields(self):
        """Test registration with missing required fields"""
        # Test without username
        invalid_data = self.test_user.copy()
        del invalid_data['username']
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='test@example.com').exists()) 
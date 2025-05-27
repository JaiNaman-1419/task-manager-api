from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserModelExtensionTest(TestCase):
    """Additional tests for User model extensions"""

    def test_user_email_as_username(self):
        """Test that email can be used as username for authentication"""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Test that USERNAME_FIELD is set to email
        self.assertEqual(User.USERNAME_FIELD, "email")

        # Test authentication with email
        from django.contrib.auth import authenticate

        authenticated_user = authenticate(
            username="test@example.com", password="testpass123"  # Using email as username
        )
        self.assertEqual(authenticated_user, user)

    def test_user_role_choices(self):
        """Test user role choices"""
        # Test default role
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.role, "user")

        # Test admin role
        admin = User.objects.create_user(
            username="admin", email="admin@example.com", password="testpass123", role="admin"
        )
        self.assertEqual(admin.role, "admin")


class TokenRefreshTest(APITestCase):
    """Test JWT token refresh functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_token_refresh(self):
        """Test refreshing access token"""
        refresh = RefreshToken.for_user(self.user)

        url = reverse("token_refresh")
        data = {"refresh": str(refresh)}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid(self):
        """Test refresh with invalid token"""
        url = reverse("token_refresh")
        data = {"refresh": "invalid_token"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

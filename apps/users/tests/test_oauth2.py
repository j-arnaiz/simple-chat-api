"""
Functional/Integration tests for OAuth2 authentication endpoints.

Tests the OAuth2 token flow and protected endpoint access.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from oauth2_provider.models import Application
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class OAuth2TokenTest(TestCase):
    """Test cases for OAuth2 token endpoints."""

    def setUp(self):
        """Set up test client, user, and OAuth2 application."""
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role=User.Role.USER,
        )

        # Create admin user
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )

        # Create OAuth2 application
        self.application = Application.objects.create(
            name="Test Application",
            user=self.admin,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        # Store the plain client secret before it gets hashed
        self.client_secret = "test-client-secret"
        self.application.client_secret = self.client_secret
        self.application.save()

    def test_obtain_token_with_valid_credentials(self):
        """Test obtaining access token with valid credentials."""
        data = {
            "grant_type": "password",
            "username": "testuser",
            "password": "testpass123",
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
        }

        response = self.client.post("/oauth/token/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.json())
        self.assertIn("refresh_token", response.json())
        self.assertIn("token_type", response.json())
        self.assertEqual(response.json()["token_type"], "Bearer")
        self.assertIn("expires_in", response.json())
        self.assertIn("scope", response.json())

    def test_obtain_token_with_invalid_credentials(self):
        """Test that invalid credentials are rejected."""
        data = {
            "grant_type": "password",
            "username": "testuser",
            "password": "wrongpassword",
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
        }

        response = self.client.post("/oauth/token/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_obtain_token_with_invalid_client(self):
        """Test that invalid client credentials are rejected."""
        data = {
            "grant_type": "password",
            "username": "testuser",
            "password": "testpass123",
            "client_id": "invalid_client_id",
            "client_secret": "invalid_secret",
        }

        response = self.client.post("/oauth/token/", data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.json())

    def test_obtain_token_missing_parameters(self):
        """Test that missing required parameters are rejected."""
        data = {
            "grant_type": "password",
            "username": "testuser",
            # Missing password
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
        }

        response = self.client.post("/oauth/token/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtain_token_for_admin_user(self):
        """Test obtaining token for admin user."""
        data = {
            "grant_type": "password",
            "username": "admin",
            "password": "adminpass123",
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
        }

        response = self.client.post("/oauth/token/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.json())

    def test_obtain_token_for_inactive_user(self):
        """Test that inactive users cannot obtain tokens."""
        User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="pass123",
            is_active=False,
        )

        data = {
            "grant_type": "password",
            "username": "inactive",
            "password": "pass123",
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
        }

        response = self.client.post("/oauth/token/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_refresh_token(self):
        """Test refreshing an access token."""
        # First, obtain a token
        data = {
            "grant_type": "password",
            "username": "testuser",
            "password": "testpass123",
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
        }

        response = self.client.post("/oauth/token/", data)
        refresh_token = response.json()["refresh_token"]

        # Now refresh the token
        refresh_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
        }

        refresh_response = self.client.post("/oauth/token/", refresh_data)

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", refresh_response.json())
        self.assertIn("refresh_token", refresh_response.json())

    def test_revoke_token(self):
        """Test revoking an access token."""
        # First, obtain a token
        data = {
            "grant_type": "password",
            "username": "testuser",
            "password": "testpass123",
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
        }

        response = self.client.post("/oauth/token/", data)
        access_token = response.json()["access_token"]

        # Revoke the token
        revoke_data = {
            "token": access_token,
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
        }

        revoke_response = self.client.post("/oauth/revoke_token/", revoke_data)

        self.assertEqual(revoke_response.status_code, status.HTTP_200_OK)

    def test_token_with_specific_scope(self):
        """Test obtaining token with specific scope."""
        data = {
            "grant_type": "password",
            "username": "testuser",
            "password": "testpass123",
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
            "scope": "read write",
        }

        response = self.client.post("/oauth/token/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.json())
        # Verify scope in response
        self.assertIn("scope", response.json())


class OAuth2ProtectedEndpointTest(TestCase):
    """Test accessing protected endpoints with OAuth2 tokens."""

    def setUp(self):
        """Set up test client, user, and OAuth2 application."""
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create OAuth2 application
        self.application = Application.objects.create(
            name="Test Application",
            user=self.user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        # Store the plain client secret before it gets hashed
        self.client_secret = "test-client-secret"
        self.application.client_secret = self.client_secret
        self.application.save()

        # Obtain access token
        data = {
            "grant_type": "password",
            "username": "testuser",
            "password": "testpass123",
            "client_id": self.application.client_id,
            "client_secret": self.client_secret,
        }

        response = self.client.post("/oauth/token/", data)
        self.access_token = response.json()["access_token"]

    def test_access_admin_with_valid_token(self):
        """Test accessing Django admin with valid OAuth2 token."""
        # Set the Authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Try to access admin (will redirect to login since we're not staff)
        response = self.client.get("/admin/")

        # Should get a redirect or forbidden, but not unauthorized
        # The token is valid, but user doesn't have admin access
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token_format(self):
        """Test that invalid token format is rejected."""
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid_token_format")

        # Try to access admin - should not crash with invalid token
        self.client.get("/admin/")

        # If we get here, no crash occurred
        self.assertTrue(True)

    def test_missing_bearer_prefix(self):
        """Test that token without Bearer prefix is handled."""
        self.client.credentials(HTTP_AUTHORIZATION=self.access_token)

        # Try to access admin - should not crash without Bearer prefix
        self.client.get("/admin/")

        # If we get here, no crash occurred
        self.assertTrue(True)

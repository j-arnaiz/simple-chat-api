"""
Tests for GraphQL authentication with OAuth2.

Tests GraphQL queries with OAuth2 tokens.
"""

import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application

User = get_user_model()


class GraphQLAuthenticationTest(TestCase):
    """Test cases for GraphQL queries with OAuth2 authentication."""

    def setUp(self):
        """Set up test users, OAuth2 application, and tokens."""
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="pass123",
            role=User.Role.USER,
        )
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )

        # Create OAuth2 application for testing
        self.application = Application.objects.create(
            name="Test Application",
            user=self.admin_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )

        # Create access tokens
        self.regular_token = AccessToken.objects.create(
            user=self.regular_user,
            application=self.application,
            token="regular-token-123",
            expires=timezone.now() + timedelta(hours=1),
            scope="read write",
        )

        self.admin_token = AccessToken.objects.create(
            user=self.admin_user,
            application=self.application,
            token="admin-token-456",
            expires=timezone.now() + timedelta(hours=1),
            scope="read write",
        )

    def test_graphql_query_with_valid_oauth2_token(self):
        """Test GraphQL query with valid OAuth2 token."""
        query = """
            query {
                users {
                    username
                    role
                }
            }
        """

        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": query}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.regular_token.token}",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsNone(data.get("errors"))
        self.assertIn("data", data)

    def test_graphql_query_with_admin_oauth2_token(self):
        """Test GraphQL query with admin OAuth2 token."""
        query = """
            query {
                users {
                    username
                    role
                }
            }
        """

        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": query}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token.token}",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsNone(data.get("errors"))

    def test_graphql_query_with_invalid_token(self):
        """Test GraphQL query with invalid OAuth2 token."""
        query = """
            query {
                users {
                    username
                }
            }
        """

        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": query}),
            content_type="application/json",
            HTTP_AUTHORIZATION="Bearer invalid-token-xyz",
        )

        # Currently no auth is enforced, so this should still work
        # In future when auth is enforced, this should return 401 or error
        self.assertEqual(response.status_code, 200)

    def test_graphql_query_with_expired_token(self):
        """Test GraphQL query with expired OAuth2 token."""
        expired_token = AccessToken.objects.create(
            user=self.regular_user,
            application=self.application,
            token="expired-token-789",
            expires=timezone.now() - timedelta(hours=1),  # Expired
            scope="read write",
        )

        query = """
            query {
                users {
                    username
                }
            }
        """

        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": query}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {expired_token.token}",
        )

        # Currently no auth is enforced, so this should still work
        # In future when auth is enforced, this should fail
        self.assertEqual(response.status_code, 200)

    def test_graphql_query_without_authentication(self):
        """Test GraphQL query without authentication header."""
        query = """
            query {
                users {
                    username
                }
            }
        """

        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": query}),
            content_type="application/json",
        )

        # Currently no auth is required, so this should work
        # In future when auth is enforced, this should return 401
        self.assertEqual(response.status_code, 200)

    def test_oauth2_token_is_not_expired(self):
        """Test that OAuth2 token validity check works."""
        self.assertFalse(self.regular_token.is_expired())
        self.assertFalse(self.admin_token.is_expired())

    def test_oauth2_token_belongs_to_correct_user(self):
        """Test that OAuth2 tokens are associated with correct users."""
        self.assertEqual(self.regular_token.user, self.regular_user)
        self.assertEqual(self.admin_token.user, self.admin_user)
        self.assertFalse(self.regular_token.user.is_admin)
        self.assertTrue(self.admin_token.user.is_admin)

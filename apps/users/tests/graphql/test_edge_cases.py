"""
Tests for GraphQL edge cases and error handling.

Tests edge cases, boundary conditions, and error handling.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client

from config.schema import schema

User = get_user_model()


class GraphQLEdgeCasesTest(TestCase):
    """Test edge cases and error handling in GraphQL."""

    def setUp(self):
        """Set up test client."""
        self.client_graphql = Client(schema)

    def test_query_user_with_negative_id(self):
        """Test querying user with negative ID."""
        query = """
            query {
                user(id: -1) {
                    id
                    username
                }
            }
        """

        result = self.client_graphql.execute(query)

        self.assertIsNone(result.get("errors"))
        self.assertIsNone(result["data"]["user"])

    def test_query_user_with_zero_id(self):
        """Test querying user with ID zero."""
        query = """
            query {
                user(id: 0) {
                    id
                    username
                }
            }
        """

        result = self.client_graphql.execute(query)

        self.assertIsNone(result.get("errors"))
        self.assertIsNone(result["data"]["user"])

    def test_query_with_very_large_id(self):
        """Test querying user with very large ID."""
        query = """
            query {
                user(id: 999999999) {
                    id
                    username
                }
            }
        """

        result = self.client_graphql.execute(query)

        self.assertIsNone(result.get("errors"))
        self.assertIsNone(result["data"]["user"])

    def test_users_query_with_inactive_users(self):
        """Test that users query handles inactive users correctly."""
        User.objects.create_user(
            username="active", email="active@example.com", password="pass123", is_active=True
        )
        User.objects.create_user(
            username="inactive", email="inactive@example.com", password="pass123", is_active=False
        )

        query = """
            query {
                users {
                    username
                    isActive
                }
            }
        """

        result = self.client_graphql.execute(query)

        self.assertIsNone(result.get("errors"))
        users = result["data"]["users"]
        self.assertEqual(len(users), 2)

        # Both should be returned
        usernames = [u["username"] for u in users]
        self.assertIn("active", usernames)
        self.assertIn("inactive", usernames)

    def test_user_type_with_null_optional_fields(self):
        """Test UserType with users that have null optional fields."""
        user = User.objects.create_user(
            username="minimal",
            email="minimal@example.com",
            password="pass123",
            first_name="",  # Empty string
            last_name="",  # Empty string
        )

        query = """
            query {
                user(id: %d) {
                    id
                    username
                    firstName
                    lastName
                }
            }
        """ % user.id

        result = self.client_graphql.execute(query)

        self.assertIsNone(result.get("errors"))
        user_data = result["data"]["user"]
        self.assertEqual(user_data["firstName"], "")
        self.assertEqual(user_data["lastName"], "")

    def test_multiple_queries_in_sequence(self):
        """Test executing multiple queries in sequence."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

        # First query
        query1 = """
            query {
                users {
                    username
                }
            }
        """

        result1 = self.client_graphql.execute(query1)
        self.assertIsNone(result1.get("errors"))

        # Second query
        query2 = """
            query {
                user(id: %d) {
                    username
                }
            }
        """ % user.id

        result2 = self.client_graphql.execute(query2)
        self.assertIsNone(result2.get("errors"))
        self.assertEqual(result2["data"]["user"]["username"], "testuser")

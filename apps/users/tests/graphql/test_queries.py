"""
Tests for GraphQL User queries.

Tests the users and user(id) GraphQL queries.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client

from config.schema import schema

User = get_user_model()


class UsersQueryTest(TestCase):
    """Test cases for the users query."""

    def setUp(self):
        """Set up test client and test users."""
        self.client = Client(schema)

    def test_users_query_returns_all_users(self):
        """Test that users query returns all users in database."""
        # Create multiple users
        User.objects.create_user(username="user1", email="user1@example.com", password="pass123")
        User.objects.create_user(username="user2", email="user2@example.com", password="pass123")
        User.objects.create_user(username="user3", email="user3@example.com", password="pass123")

        query = """
            query {
                users {
                    id
                    username
                    email
                }
            }
        """

        result = self.client.execute(query)

        self.assertIsNone(result.get("errors"))
        users = result["data"]["users"]

        self.assertEqual(len(users), 3)
        usernames = [user["username"] for user in users]
        self.assertIn("user1", usernames)
        self.assertIn("user2", usernames)
        self.assertIn("user3", usernames)

    def test_users_query_with_empty_database(self):
        """Test users query when database is empty."""
        query = """
            query {
                users {
                    id
                    username
                }
            }
        """

        result = self.client.execute(query)

        self.assertIsNone(result.get("errors"))
        users = result["data"]["users"]
        self.assertEqual(len(users), 0)

    def test_users_query_returns_both_active_and_inactive_users(self):
        """Test that users query returns both active and inactive users."""
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

        result = self.client.execute(query)

        self.assertIsNone(result.get("errors"))
        users = result["data"]["users"]

        self.assertEqual(len(users), 2)
        active_user = next(u for u in users if u["username"] == "active")
        inactive_user = next(u for u in users if u["username"] == "inactive")

        self.assertTrue(active_user["isActive"])
        self.assertFalse(inactive_user["isActive"])

    def test_users_query_includes_all_roles(self):
        """Test that users query returns users with different roles."""
        User.objects.create_user(
            username="regular", email="regular@example.com", password="pass123", role=User.Role.USER
        )
        User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="pass123",
            role=User.Role.ADMIN,
        )

        query = """
            query {
                users {
                    username
                    role
                }
            }
        """

        result = self.client.execute(query)

        self.assertIsNone(result.get("errors"))
        users = result["data"]["users"]

        self.assertEqual(len(users), 2)
        regular_user = next(u for u in users if u["username"] == "regular")
        admin_user = next(u for u in users if u["username"] == "admin")

        self.assertEqual(regular_user["role"], "user")
        self.assertEqual(admin_user["role"], "admin")


class UserQueryTest(TestCase):
    """Test cases for the user(id) query."""

    def setUp(self):
        """Set up test client and test user."""
        self.client = Client(schema)
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_user_query_returns_specific_user(self):
        """Test that user query returns specific user by ID."""
        query = """
            query {
                user(id: %d) {
                    id
                    username
                    email
                }
            }
        """ % self.user.id

        result = self.client.execute(query)

        self.assertIsNone(result.get("errors"))
        user_data = result["data"]["user"]

        self.assertEqual(user_data["id"], str(self.user.id))
        self.assertEqual(user_data["username"], "testuser")
        self.assertEqual(user_data["email"], "test@example.com")

    def test_user_query_with_nonexistent_id_returns_null(self):
        """Test that user query returns null for non-existent ID."""
        query = """
            query {
                user(id: 99999) {
                    id
                    username
                }
            }
        """

        result = self.client.execute(query)

        self.assertIsNone(result.get("errors"))
        self.assertIsNone(result["data"]["user"])

    def test_user_query_requires_id_parameter(self):
        """Test that user query requires id parameter."""
        query = """
            query {
                user {
                    id
                    username
                }
            }
        """

        result = self.client.execute(query)

        # Should have errors because id parameter is required
        self.assertIsNotNone(result.get("errors"))

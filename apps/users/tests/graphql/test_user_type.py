"""
Tests for UserType GraphQL serialization.

Tests the UserType serialization and field exposure.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client

from config.schema import schema

User = get_user_model()


class UserTypeSerializationTest(TestCase):
    """Test cases for UserType serialization."""

    def setUp(self):
        """Set up test client and test user."""
        self.client = Client(schema)
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            role=User.Role.USER,
        )

    def test_user_type_includes_expected_fields(self):
        """Test that UserType serializes all expected fields."""
        query = """
            query {
                user(id: %d) {
                    id
                    username
                    email
                    firstName
                    lastName
                    role
                    isActive
                    dateJoined
                }
            }
        """ % self.user.id

        result = self.client.execute(query)

        self.assertIsNone(result.get("errors"))
        user_data = result["data"]["user"]

        self.assertEqual(user_data["id"], str(self.user.id))
        self.assertEqual(user_data["username"], "testuser")
        self.assertEqual(user_data["email"], "test@example.com")
        self.assertEqual(user_data["firstName"], "Test")
        self.assertEqual(user_data["lastName"], "User")
        self.assertEqual(user_data["role"], "user")
        self.assertTrue(user_data["isActive"])
        self.assertIsNotNone(user_data["dateJoined"])

    def test_user_type_does_not_expose_password(self):
        """Test that password field is not exposed in GraphQL."""
        query = """
            query {
                user(id: %d) {
                    id
                    username
                    password
                }
            }
        """ % self.user.id

        result = self.client.execute(query)

        # Should have errors because password field doesn't exist
        self.assertIsNotNone(result.get("errors"))
        self.assertIn("password", str(result["errors"]).lower())

    def test_user_type_serializes_role_correctly(self):
        """Test that role field is serialized correctly for different roles."""
        admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )

        query_user = """
            query {
                user(id: %d) {
                    role
                }
            }
        """ % self.user.id

        query_admin = """
            query {
                user(id: %d) {
                    role
                }
            }
        """ % admin.id

        result_user = self.client.execute(query_user)
        result_admin = self.client.execute(query_admin)

        self.assertEqual(result_user["data"]["user"]["role"], "user")
        self.assertEqual(result_admin["data"]["user"]["role"], "admin")

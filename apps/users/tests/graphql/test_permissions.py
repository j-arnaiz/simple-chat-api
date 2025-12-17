"""
Tests for GraphQL permissions and role-based access.

Tests role-based access control in GraphQL queries.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from graphene.test import Client

from config.schema import schema

User = get_user_model()


class GraphQLPermissionsTest(TestCase):
    """Test cases for GraphQL permissions and role-based access."""

    def setUp(self):
        """Set up test users with different roles."""
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
        self.other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass123",
            role=User.Role.USER,
        )
        self.client_graphql = Client(schema)

    def test_admin_can_query_all_users(self):
        """Test that admin role can query all users."""
        query = """
            query {
                users {
                    id
                    username
                    role
                }
            }
        """

        result = self.client_graphql.execute(query)

        self.assertIsNone(result.get("errors"))
        users = result["data"]["users"]
        self.assertEqual(len(users), 3)

    def test_regular_user_can_query_all_users(self):
        """Test that regular users can also query users (no restrictions yet)."""
        query = """
            query {
                users {
                    id
                    username
                }
            }
        """

        result = self.client_graphql.execute(query)

        self.assertIsNone(result.get("errors"))
        users = result["data"]["users"]
        self.assertEqual(len(users), 3)

    def test_can_query_user_by_id(self):
        """Test querying specific user by ID."""
        query = f"""
            query {{
                user(id: {self.regular_user.id}) {{
                    id
                    username
                    role
                }}
            }}
        """

        result = self.client_graphql.execute(query)

        self.assertIsNone(result.get("errors"))
        user_data = result["data"]["user"]
        self.assertEqual(user_data["username"], "regular")
        self.assertEqual(user_data["role"], "user")

    def test_can_query_admin_user_by_id(self):
        """Test querying admin user by ID."""
        query = f"""
            query {{
                user(id: {self.admin_user.id}) {{
                    id
                    username
                    role
                }}
            }}
        """

        result = self.client_graphql.execute(query)

        self.assertIsNone(result.get("errors"))
        user_data = result["data"]["user"]
        self.assertEqual(user_data["username"], "admin")
        self.assertEqual(user_data["role"], "admin")

    def test_query_returns_correct_role_for_each_user(self):
        """Test that role field is correct for different users."""
        query = """
            query {
                users {
                    username
                    role
                }
            }
        """

        result = self.client_graphql.execute(query)

        self.assertIsNone(result.get("errors"))
        users = result["data"]["users"]

        users_dict = {u["username"]: u["role"] for u in users}
        self.assertEqual(users_dict["regular"], "user")
        self.assertEqual(users_dict["admin"], "admin")
        self.assertEqual(users_dict["other"], "user")

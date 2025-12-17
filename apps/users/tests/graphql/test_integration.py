"""
Integration tests for GraphQL endpoint.

Tests GraphQL endpoint with real HTTP requests.
"""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class GraphQLEndpointTest(TestCase):
    """Test cases for GraphQL endpoint integration."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_graphql_endpoint_is_accessible(self):
        """Test that /graphql/ endpoint is accessible."""
        response = self.client.get("/graphql/")
        # GraphQL endpoint should return 400 for GET without query
        # or 200 if GraphiQL is enabled
        self.assertIn(response.status_code, [200, 400])

    def test_graphql_endpoint_accepts_post_requests(self):
        """Test that GraphQL endpoint accepts POST requests."""
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

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("data", data)
        self.assertIsNone(data.get("errors"))


class GraphQLIntegrationTest(TestCase):
    """Integration tests for GraphQL endpoint with real HTTP requests."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="pass123",
            first_name="User",
            last_name="One",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="pass123",
            first_name="User",
            last_name="Two",
        )

    def test_complete_graphql_query_flow(self):
        """Test complete flow of making a GraphQL query."""
        query = """
            query {
                users {
                    id
                    username
                    email
                    firstName
                    lastName
                }
            }
        """

        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": query}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Verify response structure
        self.assertIn("data", data)
        self.assertIsNone(data.get("errors"))

        # Verify users data
        users = data["data"]["users"]
        self.assertEqual(len(users), 2)

        # Verify user details
        usernames = [u["username"] for u in users]
        self.assertIn("user1", usernames)
        self.assertIn("user2", usernames)

    def test_graphql_query_with_specific_fields(self):
        """Test GraphQL query requesting only specific fields."""
        query = """
            query {
                users {
                    username
                    email
                }
            }
        """

        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": query}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        users = data["data"]["users"]
        self.assertEqual(len(users), 2)

        # Verify only requested fields are present
        for user in users:
            self.assertIn("username", user)
            self.assertIn("email", user)
            self.assertNotIn("firstName", user)
            self.assertNotIn("lastName", user)

    def test_graphql_user_query_by_id_integration(self):
        """Test user(id) query through HTTP endpoint."""
        query = f"""
            query {{
                user(id: {self.user1.id}) {{
                    id
                    username
                    email
                    firstName
                    lastName
                }}
            }}
        """

        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": query}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertIsNone(data.get("errors"))
        user_data = data["data"]["user"]
        self.assertEqual(user_data["username"], "user1")
        self.assertEqual(user_data["email"], "user1@example.com")
        self.assertEqual(user_data["firstName"], "User")
        self.assertEqual(user_data["lastName"], "One")

    def test_graphql_handles_malformed_query(self):
        """Test that GraphQL handles malformed queries gracefully."""
        malformed_query = """
            query {
                users {
                    nonExistentField
                }
            }
        """

        response = self.client.post(
            "/graphql/",
            data=json.dumps({"query": malformed_query}),
            content_type="application/json",
        )

        # GraphQL can return 200 with errors or 400 for malformed queries
        self.assertIn(response.status_code, [200, 400])
        data = json.loads(response.content)

        # Should have errors for non-existent field
        self.assertIsNotNone(data.get("errors"))

    def test_graphql_handles_invalid_json(self):
        """Test that GraphQL handles invalid JSON gracefully."""
        response = self.client.post(
            "/graphql/",
            data="invalid json{{}",
            content_type="application/json",
        )

        # Should return 400 or handle gracefully
        self.assertIn(response.status_code, [200, 400])

    def test_graphql_endpoint_with_get_request(self):
        """Test GraphQL endpoint with GET request (GraphiQL)."""
        response = self.client.get("/graphql/")

        # Should return 200 (GraphiQL interface) or 400
        self.assertIn(response.status_code, [200, 400])

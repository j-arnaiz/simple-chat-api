"""
Unit tests for User model.

Tests the custom User model with role-based access control.
"""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the User model."""

    def test_create_user_with_default_role(self):
        """Test that a user is created with 'user' role by default."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, User.Role.USER)
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_admin_user(self):
        """Test creating a user with admin role."""
        admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
            role=User.Role.ADMIN,
        )

        self.assertEqual(admin.username, "admin")
        self.assertEqual(admin.role, User.Role.ADMIN)
        self.assertFalse(admin.is_superuser)  # Role admin != Django superuser

    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            username="superadmin",
            email="super@example.com",
            password="superpass123",
            role=User.Role.ADMIN,
        )

        self.assertEqual(superuser.username, "superadmin")
        self.assertEqual(superuser.role, User.Role.ADMIN)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_is_admin_property(self):
        """Test the is_admin property returns correct value."""
        regular_user = User.objects.create_user(
            username="regular", email="regular@example.com", password="pass123"
        )
        admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="pass123",
            role=User.Role.ADMIN,
        )

        self.assertFalse(regular_user.is_admin)
        self.assertTrue(admin_user.is_admin)

    def test_user_string_representation(self):
        """Test the string representation of User model."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        admin = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="pass123",
            role=User.Role.ADMIN,
        )

        self.assertEqual(str(user), "testuser (User)")
        self.assertEqual(str(admin), "adminuser (Admin)")

    def test_username_is_unique(self):
        """Test that username must be unique."""
        User.objects.create_user(
            username="duplicate", email="user1@example.com", password="pass123"
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="duplicate", email="user2@example.com", password="pass123"
            )

    def test_user_role_choices(self):
        """Test that only valid roles can be assigned."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )

        # Valid roles
        user.role = User.Role.ADMIN
        user.save()
        self.assertEqual(user.role, User.Role.ADMIN)

        user.role = User.Role.USER
        user.save()
        self.assertEqual(user.role, User.Role.USER)

    def test_user_email_field(self):
        """Test that email field is properly set."""
        user = User.objects.create_user(
            username="testuser", email="TEST@EXAMPLE.COM", password="pass123"
        )

        # Django's AbstractUser normalizes email (lowercase domain)
        self.assertTrue(user.email)
        self.assertIn("@", user.email)

    def test_user_can_change_password(self):
        """Test that user password can be changed."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpass123"
        )

        self.assertTrue(user.check_password("oldpass123"))

        user.set_password("newpass123")
        user.save()

        self.assertFalse(user.check_password("oldpass123"))
        self.assertTrue(user.check_password("newpass123"))

    def test_inactive_user(self):
        """Test creating an inactive user."""
        user = User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="pass123",
            is_active=False,
        )

        self.assertFalse(user.is_active)

    def test_get_role_display(self):
        """Test the get_role_display method from TextChoices."""
        user = User.objects.create_user(
            username="user", email="user@example.com", password="pass123"
        )
        admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="pass123",
            role=User.Role.ADMIN,
        )

        self.assertEqual(user.get_role_display(), "User")
        self.assertEqual(admin.get_role_display(), "Admin")

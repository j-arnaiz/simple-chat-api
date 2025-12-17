import graphene
from graphene_django import DjangoObjectType

from apps.users.models import User


class UserType(DjangoObjectType):
    """GraphQL type for User model."""

    role = graphene.String()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "date_joined",
        )

    def resolve_role(self, info):
        """Return role in lowercase for consistency."""
        return self.role.lower() if self.role else None


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int(required=True))

    def resolve_users(self, info):
        """Return all users."""
        return User.objects.all()

    def resolve_user(self, info, id):
        """Return a single user by ID."""
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None

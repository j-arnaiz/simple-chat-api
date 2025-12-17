import graphene

from apps.users.schema import Query as UsersQuery


class Query(UsersQuery, graphene.ObjectType):
    """Root GraphQL query combining all app queries."""

    pass


schema = graphene.Schema(query=Query)

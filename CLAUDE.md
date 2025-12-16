# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Simple Chat API is a real-time chat system built with Django, GraphQL, and WebSockets. The API uses GraphQL for all operations except OAuth2 authentication endpoints, which use REST. It implements role-based access control (admin/user) and allows users to participate in multiple named chat rooms with assignment-based access.

## Technology Stack

- Django + Django REST Framework (OAuth2 only)
- GraphQL (Graphene-Django) - primary API
- Django Channels (WebSockets)
- PostgreSQL
- OAuth2 authentication
- uv (package manager)
- Ruff + Black (code quality)

## Development Commands

```bash
# Package management (use uv, not pip)
uv pip install <package>
uv pip install -r requirements.txt
uv pip freeze > requirements.txt

# Database
python manage.py makemigrations
python manage.py migrate

# Run development server
python manage.py runserver

# Testing
python manage.py test
python manage.py test apps.chats.tests  # specific app

# Code quality
black .                          # format code
ruff check .                     # lint
ruff check --fix .              # auto-fix issues
pre-commit run --all-files      # run all hooks

# Create superuser
python manage.py createsuperuser
```

## Project Structure

The project follows a modular app structure:
- `config/`: Django settings and main configuration
- `apps/users/`: User management, authentication (OAuth2), and roles
- `apps/chats/`: Chat room models and GraphQL schema
- `apps/messaging/`: Message handling and WebSocket consumers

## Key Architecture Decisions

**API Design**: GraphQL is used for all operations (queries, mutations) except OAuth2 token endpoints which remain REST-based.

**Authentication**: OAuth2 tokens are used for both GraphQL and WebSocket connections. Token endpoints use REST.

**Access Control**: Users can only access chats they are explicitly assigned to through the ChatMembership model.

**Real-time Updates**: Django Channels handles WebSocket connections for instant message delivery.

**Package Management**: Use `uv` instead of `pip` for faster dependency resolution and installation.

**Code Quality**: Ruff for linting, Black for formatting. Pre-commit hooks enforce quality standards.

## Core Models

- **User**: Extended Django user with role field (admin/user)
- **Chat**: Named chat rooms
- **ChatMembership**: Many-to-many relationship with access control
- **Message**: Chat messages with sender and timestamp

## Testing

Django's built-in test framework is used. Tests are located in `tests.py` files within each app. Use `python manage.py test` to run the test suite.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Simple Chat API is a real-time chat system built with Django, GraphQL, and WebSockets. The API uses GraphQL for all operations except OAuth2 authentication endpoints, which use REST. It implements role-based access control (admin/user) and allows users to participate in multiple named chat rooms with assignment-based access.

## Technology Stack

- Docker + docker-compose (required for all development)
- Django + Django REST Framework (OAuth2 only)
- GraphQL (Graphene-Django) - primary API
- Django Channels (WebSockets)
- PostgreSQL
- OAuth2 authentication
- uv (package manager)
- Ruff + Black (code quality)

## Docker Setup

**IMPORTANT**: All development must be done using Docker and docker-compose. All commands (tests, migrations, code quality checks, etc.) must be executed inside Docker containers.

```bash
# Start all services
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop all services
docker-compose down

# Rebuild containers (after dependency changes)
docker-compose build

# View logs
docker-compose logs -f
docker-compose logs -f web  # specific service
```

## Development Commands

**All commands below must be executed inside the Docker container using `docker-compose exec`**

```bash
# Package management (use uv, not pip) - inside container
docker-compose exec web uv pip install <package>
docker-compose exec web uv pip install -r requirements.txt
docker-compose exec web uv pip freeze > requirements.txt

# Database - inside container
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Development server runs automatically with docker-compose up
# Access at http://localhost:8000

# Testing - inside container
docker-compose exec web python manage.py test
docker-compose exec web python manage.py test apps.chats.tests  # specific app

# Code quality - inside container
docker-compose exec web black .                          # format code
docker-compose exec web ruff check .                     # lint
docker-compose exec web ruff check --fix .              # auto-fix issues
docker-compose exec web pre-commit run --all-files      # run all hooks

# Create superuser - inside container
docker-compose exec web python manage.py createsuperuser

# Open a shell inside the container
docker-compose exec web bash
docker-compose exec web python manage.py shell  # Django shell
```

## Pre-Commit Guidelines

**IMPORTANT**: Before committing any code changes, ALWAYS run the following checks inside Docker:

```bash
# 1. Format code with Black
docker-compose exec api black .

# 2. Check and fix linting issues with Ruff
docker-compose exec api ruff check --fix .

# 3. Run all tests to ensure nothing is broken
docker-compose exec api python manage.py test

# 4. (Optional) Run pre-commit hooks
docker-compose exec api pre-commit run --all-files
```

**Commit Checklist**:
- ✅ Code formatted with Black
- ✅ No Ruff linting errors
- ✅ All tests passing
- ✅ No new warnings or issues

Only commit when all checks pass successfully. This ensures code quality and prevents breaking changes.

## Project Structure

The project follows a modular app structure:
- `config/`: Django settings and main configuration
- `apps/users/`: User management, authentication (OAuth2), and roles
- `apps/chats/`: Chat room models and GraphQL schema
- `apps/messaging/`: Message handling and WebSocket consumers

## Key Architecture Decisions

**Development Environment**: All development must be done using Docker and docker-compose. This ensures consistency across environments and simplifies dependency management.

**API Design**: GraphQL is used for all operations (queries, mutations) except OAuth2 token endpoints which remain REST-based.

**Authentication**: OAuth2 tokens are used for both GraphQL and WebSocket connections. Token endpoints use REST.

**Access Control**: Users can only access chats they are explicitly assigned to through the ChatMembership model.

**Real-time Updates**: Django Channels handles WebSocket connections for instant message delivery.

**Package Management**: Use `uv` instead of `pip` for faster dependency resolution and installation. All package commands must be executed inside the Docker container.

**Code Quality**: Ruff for linting, Black for formatting. Pre-commit hooks enforce quality standards. All quality checks must be run inside the Docker container.

## Core Models

- **User**: Extended Django user with role field (admin/user)
- **Chat**: Named chat rooms
- **ChatMembership**: Many-to-many relationship with access control
- **Message**: Chat messages with sender and timestamp

## Testing

Django's built-in test framework is used. Tests are located in `tests.py` files within each app. All tests must be run inside the Docker container using `docker-compose exec web python manage.py test`.

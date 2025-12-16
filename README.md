# Simple Chat API

Real-time chat API built with Django, GraphQL, and WebSockets.

## Description

This API provides a multi-user chat system with OAuth2 authentication, role-based access control, and real-time updates through WebSockets.

## Key Features

- **OAuth2 Authentication**: Secure token-based authentication
- **User Roles**: Support for admin and regular user roles
- **Named Chats**: Multiple chat rooms identified by unique names
- **Access Control**: Users can only access their assigned chats
- **Real-time Updates**: WebSockets for instant message delivery
- **GraphQL API**: Flexible queries and mutations for all data operations (except OAuth2)

## Tech Stack

- **Python 3.x**
- **Django**: Main web framework
- **GraphQL (Graphene-Django)**: Primary API interface
- **Django Channels**: WebSocket support
- **PostgreSQL**: Database
- **OAuth2**: Authentication and authorization
- **uv**: Package manager
- **Ruff + Black**: Code quality and formatting
- **Django Test Framework**: Built-in testing

## Prerequisites

**For Docker:**
- Docker
- Docker Compose

**For Local Development:**
- Python 3.8+
- PostgreSQL
- Redis (for Django Channels)
- uv (recommended) or pip

## Installation

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd simple-chat-api
```

2. Create environment file:
```bash
cp .env.example .env
# Edit .env if needed (defaults work for Docker)
```

3. Build and start services:
```bash
docker-compose up --build
```

4. Create superuser (in another terminal):
```bash
docker-compose exec api python manage.py createsuperuser
```

The application will be available at `http://localhost:8000`

**Services:**
- Django API: `http://localhost:8000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

**Useful Docker commands:**
```bash
# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api python manage.py migrate

# Run tests
docker-compose exec api python manage.py test

# Access Django shell
docker-compose exec api python manage.py shell
```

### Option 2: Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd simple-chat-api
```

2. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Set up PostgreSQL database and run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Run development server:
```bash
python manage.py runserver
```

## Development Commands

### Code Quality

```bash
# Format code with Black
black .

# Lint with Ruff
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Run pre-commit hooks
pre-commit run --all-files
```

### Testing

```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test apps.chats.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Usage

### OAuth2 Endpoints (REST)
- Token endpoint: `POST http://localhost:8000/oauth/token/`
- Revoke token: `POST http://localhost:8000/oauth/revoke_token/`

### GraphQL
- Endpoint: `http://localhost:8000/graphql/`
- GraphiQL interface available in development
- All chat, user, and message operations use GraphQL

### WebSocket
- Endpoint: `ws://localhost:8000/ws/chat/<chat_name>/`
- Requires authentication via token

## Project Structure

```
simple-chat-api/
├── manage.py
├── requirements.txt
├── pyproject.toml         # Ruff and Black configuration
├── .env.example
├── .pre-commit-config.yaml
├── config/                # Main Django configuration
├── apps/
│   ├── users/            # User management and authentication
│   ├── chats/            # Chat models and GraphQL schema
│   └── messaging/        # Messaging system and WebSocket consumers
└── README.md
```

## Core Models

- **User**: User with roles (admin/user)
- **Chat**: Chat room identified by name
- **ChatMembership**: Relationship between users and chats
- **Message**: Messages within chats

## GraphQL Schema Overview

### Queries
- `users`: List all users (admin only)
- `chats`: List user's accessible chats
- `messages(chatId: ID!)`: Get messages from a specific chat

### Mutations
- `createChat(name: String!)`: Create new chat (admin only)
- `assignUserToChat(userId: ID!, chatId: ID!)`: Assign user to chat (admin only)
- `sendMessage(chatId: ID!, content: String!)`: Send message to chat

## License

[To be defined]

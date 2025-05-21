# FastAPI Application

A FastAPI application with authentication endpoints and tests.

## Features

- User registration
- User login with JWT authentication
- User logout
- User profile management
- Role-based access control

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- Docker and Docker Compose (for running the application with PostgreSQL)

### Installation

1. Clone the repository
2. Install dependencies with Poetry:

```bash
poetry install
```

### Running the Application

You can run the application using Docker Compose:

```bash
docker-compose up -d
```

Or you can run it locally:

```bash
poetry run uvicorn app.main:app --reload
```

## Testing

The application includes tests for the authentication endpoints. To run the tests:

```bash
# Install development dependencies
poetry install --with dev

# Run the tests
poetry run pytest
```

For more information about the tests, see the [tests README](tests/README.md).

## Project Structure

- `app/`: Main application code
  - `auth/`: Authentication-related code
  - `admin/`: Admin-related code
  - `dao/`: Data Access Objects
  - `dependencies/`: FastAPI dependencies
- `tests/`: Test code
  - `conftest.py`: Test fixtures
  - `test_auth.py`: Tests for authentication endpoints
- `alembic/`: Database migrations

## Environment Variables

The application uses environment variables for configuration. See the `.env` file for the required variables.
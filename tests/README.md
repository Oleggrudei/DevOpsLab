# Auth Endpoints Tests

This directory contains tests for the authentication endpoints of the FastAPI application.

## Test Files

- `conftest.py`: Contains test fixtures for the FastAPI application and database
- `test_auth.py`: Contains test cases for the register, login, and logout endpoints

## Running the Tests

To run the tests, you need to have Poetry installed. Then, you can run the following commands:

```bash
# Install dependencies
poetry install --with dev

# Run the tests
poetry run pytest
```

## Test Cases

The tests cover the following scenarios:

### Register Endpoint
- Successful user registration
- Attempt to register a duplicate user (should fail)

### Login Endpoint
- Successful user login
- Attempt to login with invalid credentials (should fail)

### Logout Endpoint
- Successful user logout

## Test Database

The tests use an in-memory SQLite database instead of the PostgreSQL database used in production. This makes the tests faster and more isolated.

## Adding More Tests

To add more tests, you can create new test files in this directory. Make sure to follow the naming convention `test_*.py` so that pytest can discover them.
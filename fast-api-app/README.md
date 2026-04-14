# Book Management API with Authentication

A REST API for managing books built with FastAPI, SQLAlchemy, and SQLite following Test-Driven Development (TDD). Includes JWT-based authentication with password hashing.

## Features

- **Authentication**: JWT-based authentication with bcrypt password hashing
- **User Management**: Signup, login, logout, and password change
- **Token Invalidation**: API key-based token invalidation on logout
- **CRUD Operations**: Create, Read, Update, Delete books (protected)
- **Validation**: Comprehensive input validation using Pydantic
- **Error Handling**: Proper HTTP error responses
- **Testing**: Full test coverage with pytest
- **Documentation**: Automatic OpenAPI documentation at `/docs`

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|-------------------------|
| POST | `/auth/signup` | Register a new user | No |
| POST | `/auth/login` | Login and receive JWT token | No |
| POST | `/auth/logout` | Logout and invalidate current token | Yes (Bearer token) |
| POST | `/auth/change-password` | Change user password | Yes (Bearer token) |

### Book Endpoints (Protected)

| Method | Endpoint | Description | Authentication Required |
|--------|----------|-------------|-------------------------|
| POST | `/books/` | Create a new book | Yes (Bearer token) |
| GET | `/books/` | Get all books | Yes (Bearer token) |
| GET | `/books/{id}` | Get a specific book by ID | Yes (Bearer token) |
| PUT | `/books/{id}` | Update a book | Yes (Bearer token) |
| DELETE | `/books/{id}` | Delete a book | Yes (Bearer token) |

### Authentication Schema

#### Signup Request
```json
{
  "first_name": "string (1-50 chars)",
  "last_name": "string (1-50 chars)",
  "username": "string (3-50 chars, unique)",
  "password": "string (min 6 chars)"
}
```

#### Login Request
```json
{
  "username": "string",
  "password": "string"
}
```

#### Login/Signup Response
```json
{
  "access_token": "JWT token string",
  "token_type": "bearer"
}
```

### Book Schema
```json
{
  "title": "string (1-255 chars)",
  "author": "string (1-255 chars)",
  "published_year": "integer (1000-2100)",
  "isbn": "string (10-13 chars, unique)"
}
```

## Project Structure

```
fast-api-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models/
│   │   ├── book.py          # SQLAlchemy Book model
│   │   ├── user.py          # SQLAlchemy User model
│   │   └── user_api_key.py  # SQLAlchemy UserApiKey model
│   ├── schemas/
│   │   ├── book.py          # Pydantic schemas for books
│   │   └── user.py          # Pydantic schemas for users
│   ├── api/
│   │   ├── books.py         # Book API routes
│   │   ├── auth.py          # Authentication routes
│   │   └── deps.py          # Authentication dependencies
│   ├── services/
│   │   ├── book_service.py  # Book business logic
│   │   ├── user_service.py  # User business logic
│   │   └── auth_service.py  # Authentication logic
│   └── repositories/
│       ├── book_repository.py      # Book database operations
│       ├── user_repository.py      # User database operations
│       └── user_api_key_repository.py # API key operations
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_repositories.py # Repository tests
│   ├── test_services.py     # Service tests
│   ├── test_api.py          # API integration tests
│   └── test_auth.py         # Authentication tests
├── requirements.txt         # Dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your `JWT_SECRET_KEY` (generate a secure random string)
5. Run the application:
   ```bash
   cd fast-api-app
   uvicorn app.main:app --reload
   ```

## Environment Variables

Create a `.env` file with the following variables:

```
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=5
DATABASE_URL=sqlite:///./books.db
```

## Running Tests

```bash
cd fast-api-app
pytest
```

To run specific test files:
```bash
pytest tests/test_api.py
pytest tests/test_auth.py
pytest tests/test_services.py
pytest tests/test_repositories.py
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

All endpoints are automatically documented with request/response schemas and authentication requirements.

## Example Usage

### Authentication

#### Signup
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "password": "password123"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "password123"
  }'
```

Response includes `access_token` for use in subsequent requests.

### Book Operations (with Authentication)

#### Create a Book
```bash
curl -X POST "http://localhost:8000/books/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "published_year": 1925,
    "isbn": "9780743273565"
  }'
```

#### Get All Books
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/books/"
```

#### Get a Specific Book
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/books/1"
```

#### Update a Book
```bash
curl -X PUT "http://localhost:8000/books/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "The Great Gatsby (Updated)",
    "author": "F. Scott Fitzgerald",
    "published_year": 1925,
    "isbn": "9780743273565"
  }'
```

#### Delete a Book
```bash
curl -X DELETE "http://localhost:8000/books/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Logout
```bash
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Change Password
```bash
curl -X POST "http://localhost:8000/auth/change-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "current_password": "password123",
    "new_password": "newpassword456"
  }'
```

## Development

This project follows Test-Driven Development (TDD) principles:
1. Write failing tests
2. Implement minimal code to pass tests
3. Refactor while keeping tests green
4. Repeat for each feature

## Authentication Implementation Details

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Tokens**: HS256 algorithm with configurable expiration (default 5 minutes)
- **Token Invalidation**: Each JWT includes an API key stored in database; logout deletes the API key, making the token invalid
- **Security**: HTTPBearer authentication scheme with proper error responses

## License

MIT
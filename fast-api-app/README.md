# Book Management API

A REST API for managing books built with FastAPI, SQLAlchemy, and SQLite following Test-Driven Development (TDD).

## Features

- **CRUD Operations**: Create, Read, Update, Delete books
- **Validation**: Comprehensive input validation using Pydantic
- **Error Handling**: Proper HTTP error responses
- **Testing**: Full test coverage with pytest
- **Documentation**: Automatic OpenAPI documentation at `/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/books/` | Create a new book |
| GET | `/books/` | Get all books |
| GET | `/books/{id}` | Get a specific book by ID |
| PUT | `/books/{id}` | Update a book |
| DELETE | `/books/{id}` | Delete a book |

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
│   │   └── book.py          # SQLAlchemy Book model
│   ├── schemas/
│   │   └── book.py          # Pydantic schemas
│   ├── api/
│   │   └── books.py         # API routes
│   ├── services/
│   │   └── book_service.py  # Business logic
│   └── repositories/
│       └── book_repository.py # Database operations
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_repositories.py # Repository tests
│   ├── test_services.py     # Service tests
│   └── test_api.py          # API integration tests
├── requirements.txt         # Dependencies
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
4. Run the application:
   ```bash
   cd fast-api-app
   uvicorn app.main:app --reload
   ```

## Running Tests

```bash
cd fast-api-app
pytest
```

To run specific test files:
```bash
pytest tests/test_api.py
pytest tests/test_services.py
pytest tests/test_repositories.py
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Usage

### Create a Book
```bash
curl -X POST "http://localhost:8000/books/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "published_year": 1925,
    "isbn": "9780743273565"
  }'
```

### Get All Books
```bash
curl "http://localhost:8000/books/"
```

### Get a Specific Book
```bash
curl "http://localhost:8000/books/1"
```

### Update a Book
```bash
curl -X PUT "http://localhost:8000/books/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby (Updated)",
    "author": "F. Scott Fitzgerald",
    "published_year": 1925,
    "isbn": "9780743273565"
  }'
```

### Delete a Book
```bash
curl -X DELETE "http://localhost:8000/books/1"
```

## Development

This project follows Test-Driven Development (TDD) principles:
1. Write failing tests
2. Implement minimal code to pass tests
3. Refactor while keeping tests green
4. Repeat for each feature

## License

MIT
import pytest
from fastapi import HTTPException
from app.repositories.book_repository import BookRepository
from app.services.book_service import BookService
from app.schemas.book import BookCreate, BookUpdate

def test_create_book_success(db_session):
    repository = BookRepository(db_session)
    service = BookService(repository)
    
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        published_year=2023,
        isbn="1234567890123"
    )
    
    book = service.create_book(book_data)
    
    assert book.id is not None
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.published_year == 2023
    assert book.isbn == "1234567890123"

def test_create_book_duplicate_isbn(db_session):
    repository = BookRepository(db_session)
    service = BookService(repository)
    
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        published_year=2023,
        isbn="1234567890123"
    )
    
    # Create first book
    service.create_book(book_data)
    
    # Try to create second book with same ISBN
    with pytest.raises(HTTPException) as exc_info:
        service.create_book(book_data)
    
    assert exc_info.value.status_code == 400
    assert "already exists" in str(exc_info.value.detail)

def test_get_book_success(db_session):
    repository = BookRepository(db_session)
    service = BookService(repository)
    
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        published_year=2023,
        isbn="1234567890123"
    )
    
    created_book = service.create_book(book_data)
    retrieved_book = service.get_book(created_book.id)
    
    assert retrieved_book.id == created_book.id
    assert retrieved_book.title == "Test Book"

def test_get_book_not_found(db_session):
    repository = BookRepository(db_session)
    service = BookService(repository)
    
    with pytest.raises(HTTPException) as exc_info:
        service.get_book(999)  # Non-existent ID
    
    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail)

def test_get_all_books(db_session):
    repository = BookRepository(db_session)
    service = BookService(repository)
    
    # Create multiple books
    book1 = BookCreate(
        title="Book 1",
        author="Author 1",
        published_year=2020,
        isbn="1111111111111"
    )
    book2 = BookCreate(
        title="Book 2",
        author="Author 2",
        published_year=2021,
        isbn="2222222222222"
    )
    
    service.create_book(book1)
    service.create_book(book2)
    
    books = service.get_all_books()
    
    assert len(books) == 2
    assert books[0].title in ["Book 1", "Book 2"]
    assert books[1].title in ["Book 1", "Book 2"]

def test_update_book_success(db_session):
    repository = BookRepository(db_session)
    service = BookService(repository)
    
    book_data = BookCreate(
        title="Original Title",
        author="Original Author",
        published_year=2020,
        isbn="1234567890123"
    )
    
    created_book = service.create_book(book_data)
    
    update_data = BookUpdate(
        title="Updated Title",
        author="Updated Author",
        published_year=2024,
        isbn="9876543210987"
    )
    
    updated_book = service.update_book(created_book.id, update_data)
    
    assert updated_book.title == "Updated Title"
    assert updated_book.author == "Updated Author"
    assert updated_book.published_year == 2024
    assert updated_book.isbn == "9876543210987"

def test_update_book_not_found(db_session):
    repository = BookRepository(db_session)
    service = BookService(repository)
    
    update_data = BookUpdate(
        title="Updated Title",
        author="Updated Author",
        published_year=2024,
        isbn="9876543210987"
    )
    
    with pytest.raises(HTTPException) as exc_info:
        service.update_book(999, update_data)  # Non-existent ID
    
    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail)

def test_update_book_duplicate_isbn(db_session):
    repository = BookRepository(db_session)
    service = BookService(repository)
    
    # Create first book
    book1 = BookCreate(
        title="Book 1",
        author="Author 1",
        published_year=2020,
        isbn="1111111111111"
    )
    created_book1 = service.create_book(book1)
    
    # Create second book
    book2 = BookCreate(
        title="Book 2",
        author="Author 2",
        published_year=2021,
        isbn="2222222222222"
    )
    created_book2 = service.create_book(book2)
    
    # Try to update second book with first book's ISBN
    update_data = BookUpdate(
        title="Book 2 Updated",
        author="Author 2 Updated",
        published_year=2022,
        isbn="1111111111111"  # Same as book1's ISBN
    )
    
    with pytest.raises(HTTPException) as exc_info:
        service.update_book(created_book2.id, update_data)
    
    assert exc_info.value.status_code == 400
    assert "already exists" in str(exc_info.value.detail)

def test_delete_book_success(db_session):
    repository = BookRepository(db_session)
    service = BookService(repository)
    
    book_data = BookCreate(
        title="Book to Delete",
        author="Author",
        published_year=2023,
        isbn="1234567890123"
    )
    
    created_book = service.create_book(book_data)
    
    # Delete the book
    service.delete_book(created_book.id)
    
    # Verify book is deleted
    with pytest.raises(HTTPException) as exc_info:
        service.get_book(created_book.id)
    
    assert exc_info.value.status_code == 404

def test_delete_book_not_found(db_session):
    repository = BookRepository(db_session)
    service = BookService(repository)
    
    with pytest.raises(HTTPException) as exc_info:
        service.delete_book(999)  # Non-existent ID
    
    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail)
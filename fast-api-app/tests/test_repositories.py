import pytest
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookCreate

def test_create_book(db_session):
    repository = BookRepository(db_session)
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        published_year=2023,
        isbn="1234567890123"
    )
    
    book = repository.create(book_data)
    
    assert book.id is not None
    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.published_year == 2023
    assert book.isbn == "1234567890123"

def test_get_book_by_id(db_session):
    repository = BookRepository(db_session)
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        published_year=2023,
        isbn="1234567890123"
    )
    
    created_book = repository.create(book_data)
    retrieved_book = repository.get_by_id(created_book.id)
    
    assert retrieved_book is not None
    assert retrieved_book.id == created_book.id
    assert retrieved_book.title == "Test Book"

def test_get_all_books(db_session):
    repository = BookRepository(db_session)
    
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
    
    repository.create(book1)
    repository.create(book2)
    
    books = repository.get_all()
    
    assert len(books) == 2
    assert books[0].title in ["Book 1", "Book 2"]
    assert books[1].title in ["Book 1", "Book 2"]

def test_update_book(db_session):
    repository = BookRepository(db_session)
    book_data = BookCreate(
        title="Original Title",
        author="Original Author",
        published_year=2020,
        isbn="1234567890123"
    )
    
    created_book = repository.create(book_data)
    
    from app.schemas.book import BookUpdate
    update_data = BookUpdate(
        title="Updated Title",
        author="Updated Author",
        published_year=2024,
        isbn="9876543210987"
    )
    
    updated_book = repository.update(created_book.id, update_data)
    
    assert updated_book is not None
    assert updated_book.title == "Updated Title"
    assert updated_book.author == "Updated Author"
    assert updated_book.published_year == 2024
    assert updated_book.isbn == "9876543210987"

def test_delete_book(db_session):
    repository = BookRepository(db_session)
    book_data = BookCreate(
        title="Book to Delete",
        author="Author",
        published_year=2023,
        isbn="1234567890123"
    )
    
    created_book = repository.create(book_data)
    
    # Delete the book
    success = repository.delete(created_book.id)
    assert success is True
    
    # Verify book is deleted
    deleted_book = repository.get_by_id(created_book.id)
    assert deleted_book is None

def test_get_book_by_isbn(db_session):
    repository = BookRepository(db_session)
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        published_year=2023,
        isbn="1234567890123"
    )
    
    repository.create(book_data)
    
    book = repository.get_by_isbn("1234567890123")
    
    assert book is not None
    assert book.isbn == "1234567890123"
    assert book.title == "Test Book"
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from typing import List, Optional
from fastapi import HTTPException, status

class BookService:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def create_book(self, book: BookCreate) -> BookResponse:
        # Check if ISBN already exists
        existing_book = self.repository.get_by_isbn(book.isbn)
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN {book.isbn} already exists"
            )
        
        db_book = self.repository.create(book)
        return BookResponse.from_orm(db_book)

    def get_book(self, book_id: int) -> BookResponse:
        db_book = self.repository.get_by_id(book_id)
        if not db_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found"
            )
        return BookResponse.from_orm(db_book)

    def get_all_books(self) -> List[BookResponse]:
        db_books = self.repository.get_all()
        return [BookResponse.from_orm(book) for book in db_books]

    def update_book(self, book_id: int, book_update: BookUpdate) -> BookResponse:
        # Check if ISBN already exists for another book
        existing_book = self.repository.get_by_isbn(book_update.isbn)
        if existing_book and existing_book.id != book_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN {book_update.isbn} already exists"
            )
        
        db_book = self.repository.update(book_id, book_update)
        if not db_book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found"
            )
        return BookResponse.from_orm(db_book)

    def delete_book(self, book_id: int) -> None:
        success = self.repository.delete(book_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with id {book_id} not found"
            )
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
from typing import List, Optional

class BookRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, book: BookCreate) -> Book:
        db_book = Book(
            title=book.title,
            author=book.author,
            published_year=book.published_year,
            isbn=book.isbn
        )
        self.db.add(db_book)
        self.db.commit()
        self.db.refresh(db_book)
        return db_book

    def get_by_id(self, book_id: int) -> Optional[Book]:
        return self.db.query(Book).filter(Book.id == book_id).first()

    def get_all(self) -> List[Book]:
        return self.db.query(Book).all()

    def update(self, book_id: int, book_update: BookUpdate) -> Optional[Book]:
        db_book = self.get_by_id(book_id)
        if db_book:
            db_book.title = book_update.title
            db_book.author = book_update.author
            db_book.published_year = book_update.published_year
            db_book.isbn = book_update.isbn
            self.db.commit()
            self.db.refresh(db_book)
        return db_book

    def delete(self, book_id: int) -> bool:
        db_book = self.get_by_id(book_id)
        if db_book:
            self.db.delete(db_book)
            self.db.commit()
            return True
        return False

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        return self.db.query(Book).filter(Book.isbn == isbn).first()
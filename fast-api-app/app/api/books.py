from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.repositories.book_repository import BookRepository
from app.services.book_service import BookService
from app.schemas.book import BookCreate, BookUpdate, BookResponse
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/books", tags=["books"])

def get_book_service(db: Session = Depends(get_db)) -> BookService:
    repository = BookRepository(db)
    return BookService(repository)

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: BookCreate,
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user)
):
    return service.create_book(book)

@router.get("/", response_model=List[BookResponse])
def get_all_books(
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user)
):
    return service.get_all_books()

@router.get("/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user)
):
    return service.get_book(book_id)

@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user)
):
    return service.update_book(book_id, book_update)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    service: BookService = Depends(get_book_service),
    current_user: User = Depends(get_current_user)
):
    service.delete_book(book_id)
    return None
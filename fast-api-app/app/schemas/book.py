from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    published_year: int = Field(..., ge=1000, le=2100)
    isbn: str = Field(..., min_length=10, max_length=13)

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
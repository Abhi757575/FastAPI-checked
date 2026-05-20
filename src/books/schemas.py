from pydantic import BaseModel, ConfigDict
from typing import Optional
import uuid
from datetime import date, datetime
from src.reviews.schemas import ReviewModel
from typing import List

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


class Book(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime

class BookDetailModel(Book):
    reviews: List[ReviewModel]


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[date] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
from unittest import result

from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdate
from src.db.models import Book
from datetime import datetime

class BookService:
    async def get_all_books(self, session:AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.execute(statement)
        return result.scalars().all()
    
    async def get_user_book_submissions(self,user_uid: str, session:AsyncSession):
        statement = select(Book).where(Book.user_uid== user_uid).order_by(desc(Book.created_at))
        result = await session.execute(statement)
        return result.scalars().all()
    
    async def get_book(self, book_uid:str, session:AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.execute(statement)
        return result.scalars().first()

    async def create_book(self, book_data:BookCreateModel,user_uid:str, session:AsyncSession):
        book_data_dict = book_data.model_dump()

        new_book = Book(
            **book_data_dict
        )
        new_book.published_date = datetime.strptime(book_data_dict['published_date'], "%Y-%m-%d")
        new_book.user_uid = user_uid
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

    async def update_book(self, book_uid: str, update_data: BookUpdate, session: AsyncSession):
        book_to_update = await self.get_book(book_uid, session)

        if book_to_update is not None:
            
            update_book_dict = update_data.model_dump()
            for k, v in update_book_dict.items():
                setattr(book_to_update, k, v)
            
            await session.commit()
            return book_to_update
        
        elif book_to_update is None:
            return None

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return book_to_delete
        
        elif book_to_delete is None:
            return None
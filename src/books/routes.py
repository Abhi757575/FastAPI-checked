from fastapi import FastAPI, HTTPException, Header, status, Depends
from typing import Optional, List
from fastapi import APIRouter
from .schemas import (
    BookCreateModel,
    BookUpdate,
    Book as BookResponse,
    BookDetailModel
)
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.books.book_data import books
from src.db.main import get_session
from src.books.service import BookService
from sqlalchemy.ext.asyncio import AsyncSession

book_router = APIRouter()
book_Service = BookService()
access_token_bearer = AccessTokenBearer()
role_Checker = Depends(RoleChecker(['admin', 'user']))


@book_router.get("/", response_model=List[BookResponse], status_code=status.HTTP_200_OK, dependencies=[role_Checker])
async def get_all_books(session: AsyncSession = Depends(get_session), token_details = Depends(access_token_bearer)):
    #print(user_details)
    books= await book_Service.get_all_books(session)
    return books


@book_router.get("/user/{user_uid}", response_model=List[BookResponse], status_code=status.HTTP_200_OK, dependencies=[role_Checker])
async def get_user_book_submissions(user_uid: str,session: AsyncSession = Depends(get_session), token_details = Depends(access_token_bearer)):
    
    books= await book_Service.get_user_books(user_uid, session)
    return books

@book_router.post("/", response_model=BookResponse, status_code = status.HTTP_201_CREATED, dependencies=[role_Checker])
async def create_book(book_data: BookCreateModel,session: AsyncSession = Depends(get_session), token_details = Depends(access_token_bearer)) -> dict:
    user_id = token_details.get('user')['user_uid']
    new_book =await book_Service.create_book(book_data, user_id, session)
    return new_book

@book_router.get("/{book_uid}", response_model=BookDetailModel, status_code=status.HTTP_200_OK)
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session)):
    book = await book_Service.get_book(book_uid, session)
    if book:
        return book
    else:
        raise HTTPException(status_code=404, detail="Book not found")


@book_router.patch("/{book_uid}", response_model=BookResponse, status_code=status.HTTP_200_OK, dependencies=[role_Checker])
async def update_book(
    book_uid: str,
    book_update_data: BookUpdate,
    session: AsyncSession = Depends(get_session),
    user_details = Depends(access_token_bearer)
):
    updated_book = await book_Service.update_book(
        book_uid,
        book_update_data,
        session
    )

    if updated_book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return updated_book

@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_Checker])
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session), user_details = Depends(access_token_bearer)):
    book_to_delete = await book_Service.delete_book(book_uid, session)

    if book_to_delete:
        return None
    else:
        raise HTTPException(status_code=404, detail="Book not found")
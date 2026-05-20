from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse

class BooklyException(Exception):
    """This is a base class for exceptions for all bookly errors"""
    pass

class InvalidToken(BooklyException):
    """User has provided an invalid or expired token"""
    pass

class RevokedToken(BooklyException):
    """Raised when a revoked token is used."""


class AccessTokenRequired(BooklyException):
    """Raised when an access token is required."""


class RefreshTokenRequired(BooklyException):
    """Raised when a refresh token is required."""


class UserAlreadyExists(BooklyException):
    """Raised when a user already exists during signup."""


class InvalidCredentials(BooklyException):
    """Raised when invalid login credentials are provided."""


class InsufficientPermission(BooklyException):
    """Raised when a user lacks required permissions."""


class BookNotFound(BooklyException):
    """Raised when a book is not found."""


class TagNotFound(BooklyException):
    """Raised when a tag is not found."""


class TagAlreadyExists(BooklyException):
    """Raised when a tag already exists."""


class UserNotFound(BooklyException):
    """Raised when a user is not found."""


def create_exception_handler(status_code: int, initial_detail: any) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exec: BooklyException):
        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )
    
    return exception_handler

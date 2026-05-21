#it is used to mark this src as a paython package
from fastapi import FastAPI, status
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from fastapi.responses import JSONResponse
from src.auth.routers import auth_Router
from src.reviews.routes import review_Router
from src.tags.routes import tags_router # import this
from src.middleware import register_middleware
from src.errors import (
    create_exception_handler,
    InvalidCredentials,
    TagAlreadyExists,
    TagNotFound,
    UserAlreadyExistsException,
    UserNotFoundException,
    BookNotFound,
    InvalidToken,
    AccessTokenRequired,
    RefreshTokenRequired,
    InsufficientPermission,
    RevokedToken,
    register_all_errors
)


@asynccontextmanager
async def life_span(app: FastAPI):
    # Startup code
    #await init_db()  # Initialize the database connection
    print("🚀 Starting up the application...")
    from src.db.models import Book

    yield
    # Shutdown code
    print("🛑 Shutting down the application...")


version = "v1"

description = """ A Rest API for a book review web service """

app = FastAPI(
    title="Book API",
    description=description,
    version = version,
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/license/mit/"
    },
    contact={
        "name": "Abhi757575",
        "github": "https://github.com/Abhi757575"
    },
    terms_of_service="https://example.com/terms/",
    open_api_url = f"/api/{version}/openapi.json",
    docs_url = f"/api/{version}/docs",
    redoc_url = f"/api/{version}/redoc",
)

def register_error_handlers(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExistsException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "A User with email already exists",
                "error_code": "UserAlreadyExistsException",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book not found",
                "error_code": "book_not_found",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid email or password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or expired",
                "resolution": "Please get a new token",
                "error_code": "invalid_token",
            },
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get a new token",
                "error_code": "token_revoked",
            },
        ),
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get a refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have enough permissions to perform this action",
                "error_code": "insufficient_permissions",
            },
        ),
    )

    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Tag not found",
                "error_code": "tag_not_found",
            },
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "Tag already exists",
                "error_code": "tag_exists",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_Server_error (request, exc):
        return JSONResponse(
            content={
                "message": "Oops... Something went wrong",
                "error_code": "internal_server_error"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
register_middleware(app) 
register_all_errors(app)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["Books"])
app.include_router(auth_Router, prefix=f"/api/{version}/auth", tags=["Authentication"])
app.include_router(review_Router, prefix=f"/api/{version}/reviews", tags = ["Reviews"])
app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["tags"]) #add this
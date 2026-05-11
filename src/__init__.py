#it is used to mark this src as a paython package
from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db

@asynccontextmanager
async def life_span(app: FastAPI):
    # Startup code
    await init_db()  # Initialize the database connection
    print("🚀 Starting up the application...")
    yield
    # Shutdown code
    print("🛑 Shutting down the application...")


version = "v1"

app = FastAPI(
    title="Book API",
    description="A simple API to manage books",
    version = version,
    lifespan=life_span
)
app.include_router(book_router, prefix=f"/api/{version}/books", tags=["Books"])
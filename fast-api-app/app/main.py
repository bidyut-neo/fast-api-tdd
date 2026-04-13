from fastapi import FastAPI
from app.api import books
from app.database import engine, Base
import uvicorn

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Management API",
    description="A REST API for managing books with CRUD operations",
    version="1.0.0"
)

# Include routers
app.include_router(books.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Book Management API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
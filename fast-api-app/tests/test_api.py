import pytest

def test_create_book_api(client):
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "published_year": 2023,
        "isbn": "1234567890123"
    }
    
    response = client.post("/books/", json=book_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"
    assert data["published_year"] == 2023
    assert data["isbn"] == "1234567890123"
    assert "id" in data
    assert "created_at" in data

def test_create_book_validation_error(client):
    # Missing required field
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        # Missing published_year and isbn
    }
    
    response = client.post("/books/", json=book_data)
    
    assert response.status_code == 422  # Validation error

def test_get_book_api(client):
    # First create a book
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "published_year": 2023,
        "isbn": "1234567890123"
    }
    
    create_response = client.post("/books/", json=book_data)
    book_id = create_response.json()["id"]
    
    # Then retrieve it
    response = client.get(f"/books/{book_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "Test Book"

def test_get_book_not_found(client):
    response = client.get("/books/999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_get_all_books_api(client):
    # Create multiple books
    book1 = {
        "title": "Book 1",
        "author": "Author 1",
        "published_year": 2020,
        "isbn": "1111111111111"
    }
    book2 = {
        "title": "Book 2",
        "author": "Author 2",
        "published_year": 2021,
        "isbn": "2222222222222"
    }
    
    client.post("/books/", json=book1)
    client.post("/books/", json=book2)
    
    response = client.get("/books/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    
    # Check that our books are in the response
    titles = [book["title"] for book in data]
    assert "Book 1" in titles
    assert "Book 2" in titles

def test_update_book_api(client):
    # Create a book first
    book_data = {
        "title": "Original Title",
        "author": "Original Author",
        "published_year": 2020,
        "isbn": "1234567890123"
    }
    
    create_response = client.post("/books/", json=book_data)
    book_id = create_response.json()["id"]
    
    # Update the book
    update_data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "published_year": 2024,
        "isbn": "9876543210987"
    }
    
    response = client.put(f"/books/{book_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Updated Author"
    assert data["published_year"] == 2024
    assert data["isbn"] == "9876543210987"

def test_update_book_not_found(client):
    update_data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "published_year": 2024,
        "isbn": "9876543210987"
    }
    
    response = client.put("/books/999", json=update_data)
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_delete_book_api(client):
    # Create a book first
    book_data = {
        "title": "Book to Delete",
        "author": "Author",
        "published_year": 2023,
        "isbn": "1234567890123"
    }
    
    create_response = client.post("/books/", json=book_data)
    book_id = create_response.json()["id"]
    
    # Delete the book
    response = client.delete(f"/books/{book_id}")
    
    assert response.status_code == 204
    
    # Verify book is deleted
    get_response = client.get(f"/books/{book_id}")
    assert get_response.status_code == 404

def test_delete_book_not_found(client):
    response = client.delete("/books/999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_duplicate_isbn_error(client):
    book_data = {
        "title": "Book 1",
        "author": "Author 1",
        "published_year": 2020,
        "isbn": "1234567890123"
    }
    
    # Create first book
    response1 = client.post("/books/", json=book_data)
    assert response1.status_code == 201
    
    # Try to create second book with same ISBN
    book_data["title"] = "Book 2"
    response2 = client.post("/books/", json=book_data)
    
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

# Book Inventory Management API

This is a Flask-based API designed for managing a book inventory system. It allows users to create, retrieve, update, delete, and filter books using a JSON-based storage system. The API also features logging capabilities, with customizable logging levels for monitoring and troubleshooting the application's behavior.

## Features

- Add new books to the inventory.
- Retrieve all books or filter them based on criteria such as author, price range, year range, or genres.
- View detailed information for a specific book by its ID.
- Update the price of an existing book.
- Delete a book from the inventory.
- Monitor application logs and dynamically change logging levels.

## Table of Contents
1. [Installation](#installation)
2. [API Endpoints](#api-endpoints)
3. [Logging](#logging)
4. [Data Management](#data-management)
5. [Running the Application](#running-the-application)

## Installation

### Prerequisites

- Python 3.x
- Flask

### Steps

1. Clone the repository or download the project.

2. Install the required dependencies:
    ```bash
    pip install flask
    ```

3. Run the application:
    ```bash
    python app.py
    ```

The app will be available at `http://localhost:8574`.

## API Endpoints

1. **Health Check**  
   **GET** `/books/health`  
   Ensures the server is running.  
   **Response:** `OK`

2. **Add a New Book**  
   **POST** `/book`  
   Adds a new book to the inventory.  
   **Request Body (JSON):**
   ```json
   {
     "title": "Book Title",
     "author": "Author Name",
     "year": 2020,
     "price": 100,
     "genres": ["SCI_FI", "NOVEL"]
   }
   ```
   **Response:** ID of the newly created book.

3. **Get Total Books**  
   **GET** `/books/total`  
   Returns the total number of books, with optional filters.  
   **Filters:** `author`, `price-bigger-than`, `price-less-than`, `year-bigger-than`, `year-less-than`, `genres`  
   **Response:** Total number of matching books.

4. **Get Books List**  
   **GET** `/books`  
   Retrieves a list of books with optional filters and sorting.  
   **Response:** List of books matching the query.

5. **Get Book by ID**  
   **GET** `/book`  
   Retrieves details of a book by its ID.  
   **Query Parameter:** `id` (required)  
   **Response:** Book details.

6. **Update Book Price**  
   **PUT** `/book`  
   Updates the price of a book by its ID.  
   **Query Parameters:** `id`, `price` (both required)  
   **Response:** Old price of the book.

7. **Delete Book**  
   **DELETE** `/book`  
   Deletes a book by its ID.  
   **Query Parameter:** `id` (required)  
   **Response:** Total remaining books.

8. **Get Logger Level**  
   **GET** `/logs/level`  
   Retrieves the current logging level of a specified logger.  
   **Query Parameter:** `logger-name` (required)  
   **Response:** The current log level of the specified logger.

9. **Set Logger Level**  
   **PUT** `/logs/level`  
   Updates the logging level of a specified logger.  
   **Query Parameters:** `logger-name`, `logger-level` (both required)  
   **Response:** Updated log level.

## Logging

The application logs all requests and book-related events. Logs are stored in the `logs/` directory:
- `logs/requests.log`: Logs all incoming requests.
- `logs/books.log`: Logs all actions related to book operations.

### Changing Log Levels

You can dynamically change log levels by calling the `/logs/level` endpoint.

**Example:** Setting the `request-logger` level to `DEBUG`:
```bash
curl -X PUT "http://localhost:8574/logs/level?logger-name=request-logger&logger-level=DEBUG"
```

## Data Management

Books data is stored in a JSON file at `data/books.json`.  
The file is automatically created if it doesn't exist when the application starts.

### Book Data Structure
```json
{
  "id": 1,
  "title": "Book Title",
  "author": "Author Name",
  "year": 2020,
  "price": 100,
  "genres": ["SCI_FI", "NOVEL"]
}
```

## Running the Application

Ensure that all dependencies are installed and the project is set up.

### Start the Flask server:
```bash
python app.py
```
Access the API at `http://localhost:8574`.

### Running on a Different Port
By default, the application runs on port `8574`.  
You can change this by editing the last line of the script:
```python
app.run(port=<desired_port>)
```

---

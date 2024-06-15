
import json  # Import JSON module for handling JSON data
import os  # Import OS module for file path operations
import logging
import time
from collections import OrderedDict
from flask import Flask, request, jsonify, g  # Import necessary modules from Flask

app = Flask(__name__)  # Initialize the Flask application

DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'books.json')


# Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')


class MillisecondFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
            return s.replace('{msecs}', '%03d' % record.msecs)
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            return "%s.%03d" % (t, record.msecs)

request_logger = logging.getLogger('request-logger')
request_logger.setLevel(logging.INFO)
request_file_handler = logging.FileHandler('logs/requests.log')
request_file_handler.setLevel(logging.INFO)
request_console_handler = logging.StreamHandler()
request_formatter = MillisecondFormatter('%(asctime)s %(levelname)s: %(message)s | request #%(request_number)s',
                                         datefmt="%d-%m-%Y %H:%M:%S.{msecs}")
request_file_handler.setFormatter(request_formatter)
request_console_handler.setFormatter(request_formatter)
request_logger.addHandler(request_file_handler)
request_logger.addHandler(request_console_handler)

books_logger = logging.getLogger('books-logger')
books_logger.setLevel(logging.INFO)
books_file_handler = logging.FileHandler('logs/books.log')
books_file_handler.setLevel(logging.INFO)
books_formatter = MillisecondFormatter('%(asctime)s %(levelname)s: %(message)s | request #%(request_number)s',
                                       datefmt="%d-%m-%Y %H:%M:%S.{msecs}")
books_file_handler.setFormatter(books_formatter)
books_logger.addHandler(books_file_handler)


request_counter = 0

@app.before_request
def before_request():
    global request_counter
    request.start_time = time.time()
    g.start_time = time.time()
    request_counter += 1
    g.request_number = request_counter
    request_logger.info(f"Incoming request | #{request_counter} | resource: {request.path} | HTTP Verb {request.method}", extra={'request_number': request_counter})

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    request_logger.debug(f"request #{g.request_number} duration: {duration:.3f}ms",
                         extra={'request_number': g.request_number})
    return response

def load_books():
    """Load books data from the JSON file."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as file:
            json.dump([], file)
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def save_books(books):
    """Save books data to the JSON file."""
    with open(DATA_FILE, 'w') as file:
        json.dump(books, file)

def next_book_id(books):
    """Generate the next book ID based on existing books."""
    if books:
        return max(book['id'] for book in books) + 1
    return 1

def filter_books(args):
    """Filter books based on query parameters."""
    # Extract query parameters
    author = args.get('author')
    price_bigger_than = args.get('price-bigger-than', type=int)
    price_less_than = args.get('price-less-than', type=int)
    year_bigger_than = args.get('year-bigger-than', type=int)
    year_less_than = args.get('year-less-than', type=int)
    genres = args.get('genres')

    # Start with the full list of books
    filtered_books = books

    # Filter by author if provided
    if author:
        filtered_books = [book for book in filtered_books if book['author'].lower() == author.lower()]

    # Filter by price greater than or equal to if provided
    if price_bigger_than is not None:
        filtered_books = [book for book in filtered_books if book['price'] >= price_bigger_than]

    # Filter by price less than or equal to if provided
    if price_less_than is not None:
        filtered_books = [book for book in filtered_books if book['price'] <= price_less_than]

    # Filter by year greater than or equal to if provided
    if year_bigger_than is not None:
        filtered_books = [book for book in filtered_books if book['year'] >= year_bigger_than]

    # Filter by year less than or equal to if provided
    if year_less_than is not None:
        filtered_books = [book for book in filtered_books if book['year'] <= year_less_than]

    # Filter by genres if provided
    if genres:
        genres_set = set(genres.split(','))
        # Define the valid genres
        valid_genres = {"SCI_FI", "NOVEL", "HISTORY", "MANGA", "ROMANCE", "PROFESSIONAL"}
        # Check if provided genres are valid
        if not genres_set.issubset(valid_genres):
            return "Invalid genres"
        # Filter books that have any of the provided genres
        filtered_books = [book for book in filtered_books if any(genre in book['genres'] for genre in genres_set)]

    return filtered_books


books = load_books()  # Load books data at startup

@app.route('/books/health', methods=['GET'])
def health():
    """Health check endpoint to ensure the server is running."""
    return "OK", 200

@app.route('/book', methods=['POST'])
def create_book():
    """Create a new book in the inventory."""
    global books
    data = request.json
    title = data.get('title')
    author = data.get('author')
    year = data.get('year')
    price = data.get('price')
    genres = data.get('genres')

    # Check if a book with the same title already exists
    if any(book['title'].lower() == title.lower() for book in books):
        return jsonify(errorMessage=f"Error: Book with the title [{title}] already exists in the system"), 409

    # Validate the year range
    if not (1940 <= year <= 2100):
        return jsonify(errorMessage=f"Error: Can't create new Book that its year [{year}]"
                                    f" is not in the accepted range [1940 -> 2100]"), 409

    # Validate the price
    if price < 0:
        return jsonify(errorMessage="Error: Can't create new Book with negative price"), 409

    # Create a new book entry
    book_id = next_book_id(books)
    new_book = {
        'id': book_id,
        'title': title,
        'author': author,
        'year': year,
        'price': price,
        'genres': genres
    }
    books_logger.info(f"Creating new Book with Title [{title}]", extra={'request_number': g.request_number})
    books_logger.debug(f"Currently there are {len(books)} Books in the system. New Book will be assigned with id "
                       f"{book_id}", extra={'request_number': g.request_number})
    books.append(new_book)  # Add the new book to the list
    save_books(books)  # Save the updated list to the file

    return jsonify(result=book_id), 200

@app.route('/books/total', methods=['GET'])
def get_total_books():
    """Get the total number of books in the inventory, with optional filters."""
    global books
    filtered_books = filter_books(request.args)
    if isinstance(filtered_books, str):  # Check if there was an error
        return jsonify(errorMessage=filtered_books), 400
    books_logger.info(f"Total Books found for requested filters is {len(filtered_books)}",
                      extra={'request_number': g.request_number})
    return jsonify(result=len(filtered_books)), 200

@app.route('/books', methods=['GET'])
def get_books():
    """Get a list of books based on filters, sorted by title."""
    global books
    filtered_books = filter_books(request.args)
    if isinstance(filtered_books, str):  # Check if there was an error
        return jsonify(errorMessage=filtered_books), 400
    sorted_books = sorted(filtered_books, key=lambda x: x['title'].lower())
    books_logger.info(f"Total Books found for requested filters is "
                      f"{len(sorted_books)}", extra={'request_number': g.request_number})
    return jsonify(result=sorted_books), 200

@app.route('/book', methods=['GET'])
def get_book():
    """Get details of a single book by its ID."""
    global books
    book_id = int(request.args.get('id'))
    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        return jsonify(errorMessage=f"Error: no such Book with id {book_id}"), 404

    # Use OrderedDict to maintain the order of fields in the response
    books_logger.debug(f"Fetching book id {book_id} details", extra={'request_number': g.request_number})
    response_book = OrderedDict([
        ("id", book['id']),
        ("title", book['title']),
        ("author", book['author']),
        ("price", book['price']),
        ("year", book['year']),
        ("genres", book['genres'])
    ])
    return jsonify(result=response_book), 200

@app.route('/book', methods=['PUT'])
def update_book_price():
    """Update the price of a book by its ID."""
    global books
    book_id = int(request.args.get('id'))
    new_price = int(request.args.get('price'))

    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        return jsonify(errorMessage=f"Error: no such Book with id {book_id}"), 404

    if new_price < 0:
        return jsonify(errorMessage="Error: Can't update Book price to be negative"), 409

    books_logger.info(f"Update Book id [{book_id}] price to {new_price}", extra={'request_number': g.request_number})
    books_logger.debug(f"Book [{book['title']}] price change: {book['price']} --> {new_price}"
                       , extra={'request_number': g.request_number})
    old_Price = book['price']
    book['price'] = new_price
    save_books(books)  # Save the updated list to the file

    return jsonify(result=old_Price), 200

@app.route('/book', methods=['DELETE'])
def delete_book():
    """Delete a book by its ID."""
    global books
    book_id = int(request.args.get('id'))

    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        return jsonify(errorMessage=f"Error: no such Book with id {book_id}"), 404

    books_logger.info(f"Removing book [{book['title']}]", extra={'request_number': g.request_number})
    books.remove(book)
    remaining_books = len(books)
    books_logger.debug(f"After removing book [{book['title']}] id: [{book_id}] there are "
                       f"{len(books)} books in the system", extra={'request_number': g.request_number})
    save_books(books)  # Save the updated list to the file

    return jsonify(result=remaining_books), 200

@app.route('/logs/level', methods=['GET'])
def get_logger_level():
    """Get the current level of a logger."""
    logger_name = request.args.get('logger-name')
    logger = logging.getLogger(logger_name)
    if logger is None:
        return jsonify(errorMessage=f"Logger {logger_name} not found"), 404
    level_name = logging.getLevelName(logger.level)
    return level_name, 200

@app.route('/logs/level', methods=['PUT'])
def set_logger_level():
    """Set the level of a logger."""
    logger_name = request.args.get('logger-name')
    level_name = request.args.get('logger-level')
    logger = logging.getLogger(logger_name)
    if logger is None:
        return jsonify(errorMessage=f"Logger {logger_name} not found"), 404
    level = getattr(logging, level_name.upper(), None)
    if not isinstance(level, int):
        return jsonify(errorMessage=f"Invalid log level: {level_name}"), 400
    logger.setLevel(level)
    return level_name.upper(), 200

if __name__ == '__main__':
    app.run(port=8574)

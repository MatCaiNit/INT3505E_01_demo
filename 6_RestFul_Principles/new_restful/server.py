from flask import Flask, jsonify, request
from flasgger import Swagger
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Sử dụng path tuyệt đối để Flask luôn tìm được file
swagger_path = os.path.join(os.getcwd(), "openapi", "openapi.yaml")
swagger = Swagger(app, template_file=swagger_path)


books = [
    {"id": 1, "title": "Clean Code", "author_id": 1, "available": True},
    {"id": 2, "title": "The Pragmatic Programmer", "author_id": 2, "available": False},
    {"id": 3, "title": "Refactoring", "author_id": 3, "available": True},
    {"id": 4, "title": "Design Patterns", "author_id": 4, "available": True},
    {"id": 5, "title": "Python Crash Course", "author_id": 5, "available": True},
]

authors = [
    {"id": 1, "name": "Robert C. Martin"},
    {"id": 2, "name": "Andrew Hunt"},
    {"id": 3, "name": "Martin Fowler"},
    {"id": 4, "name": "Erich Gamma"},
    {"id": 5, "name": "Eric Matthes"},
]

users = [
    {"id": 1, "name": "Alice", "borrowed": [2]},
    {"id": 2, "name": "Bob", "borrowed": []},
]

# ==========================
#   RESOURCE DESIGN
# ==========================

@app.route('/')
def home():
    return jsonify({
        "message": "Library Management API",
        "resources": {
            "books": "/books",
            "authors": "/authors",
            "users": "/users"
        }
    })


# ========== BOOKS ==========
@app.route('/books', methods=['GET'])
def get_books():
    """
    GET /books?search=keyword&offset=0&limit=2
    """
    search = request.args.get('search', '').lower()
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 2))

    filtered = [b for b in books if search in b['title'].lower()]

    # Pagination
    paginated = filtered[offset: offset + limit]

    return jsonify({
        "total": len(filtered),
        "offset": offset,
        "limit": limit,
        "data": paginated
    })


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)


@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    new_id = max([b["id"] for b in books]) + 1 if books else 1
    new_book = {
        "id": new_id,
        "title": data.get("title"),
        "author_id": data.get("author_id"),
        "available": True
    }
    books.append(new_book)
    return jsonify(new_book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    book['title'] = data.get('title', book['title'])
    book['author_id'] = data.get('author_id', book['author_id'])
    return jsonify(book)


# ========== AUTHORS ==========
@app.route('/authors', methods=['GET'])
def get_authors():
    return jsonify(authors)


@app.route('/authors/<int:author_id>/books', methods=['GET'])
def get_books_by_author(author_id):
    author_books = [b for b in books if b['author_id'] == author_id]
    return jsonify(author_books)


# ========== USERS ==========
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route('/users/<int:user_id>/borrowings', methods=['GET'])
def get_user_borrowings(user_id):
    """
    Resource tree: /users/{id}/borrowings
    """
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    borrowed_books = [b for b in books if b['id'] in user['borrowed']]
    return jsonify(borrowed_books)


@app.route('/users/<int:user_id>/borrowings', methods=['POST'])
def borrow_book(user_id):
    data = request.get_json()
    book_id = data.get('book_id')

    if book_id is None:
        return jsonify({"error": "book_id is required"}), 400

    user = next((u for u in users if u['id'] == user_id), None)
    book = next((b for b in books if b['id'] == book_id), None)

    if not user:
        return jsonify({"error": "User not found"}), 404
    if not book:
        return jsonify({"error": "Book not found"}), 404
    if not book['available']:
        return jsonify({"error": "Book already borrowed"}), 400
    if book_id in user['borrowed']:
        return jsonify({"error": "User already borrowed this book"}), 400

    # Borrow book
    user['borrowed'].append(book_id)
    book['available'] = False

    return jsonify({
        "message": f"User {user['name']} borrowed {book['title']}",
        "borrowed_books": [b for b in books if b['id'] in user['borrowed']]
    })
@app.route('/users/<int:user_id>/return', methods=['POST'])
def return_book(user_id):
    data = request.get_json()
    book_id = data.get('book_id')

    user = next((u for u in users if u['id'] == user_id), None)
    book = next((b for b in books if b['id'] == book_id), None)

    if not user or not book:
        return jsonify({"error": "Invalid user or book"}), 400
    if book_id not in user['borrowed']:
        return jsonify({"error": "Book not borrowed by user"}), 400

    # Return book
    user['borrowed'].remove(book_id)
    book['available'] = True

    return jsonify({
        "message": f"User {user['name']} returned {book['title']}",
        "borrowed_books": [b for b in books if b['id'] in user['borrowed']]
    })

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Cập nhật tên
    user['name'] = data.get('name', user['name'])
    return jsonify(user)

# ==========================
#   RUN SERVER
# ==========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, jsonify, request
from flasgger import Swagger
from flask_cors import CORS
import os
from datetime import datetime

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
    {"id": 6, "title": "Đắc Nhân Tâm", "author_id": 6, "available": True},
    {"id": 7, "title": "Sự im lặng của bầy cừu", "author_id": 7, "available": True},
    {"id": 8, "title": "Tuổi trẻ đáng giá bao nhiêu", "author_id": 8, "available": False},
    {"id": 9, "title": "Nhà giả kim", "author_id": 9 , "available": True},
    {"id": 10, "title": "Đừng bao giờ từ bỏ ước mơ", "author_id": 10, "available": True},
    {"id": 11, "title": "Bí mật tư duy triệu phú", "author_id": 11, "available": False},
    {"id": 12, "title": "Đời ngắn đừng ngủ dài", "author_id": 12, "available": True},
    {"id": 13, "title": "Nhà giầu có nhất thành Babylon", "author_id": 13, "available": True},
    {"id": 14, "title": "7 thói quen của người thành đạt", "author_id": 14, "available": True},
    {"id": 15, "title": "Đừng để con rùa chết khát", "author_id": 15, "available": False},
    {"id": 16, "title": "Dạy con làm giàu", "author_id": 16, "available": True},  
]

authors = [
    {"id": 1, "name": "Robert C. Martin"},
    {"id": 2, "name": "Andrew Hunt"},
    {"id": 3, "name": "Martin Fowler"},
    {"id": 4, "name": "Erich Gamma"},
    {"id": 5, "name": "Eric Matthes"},
    {"id": 6, "name": "Dale Carnegie"},
    {"id": 7, "name": "Thomas Harris"},
    {"id": 8, "name": "Rosie Nguyễn"},
    {"id": 9, "name": "Paulo Coelho"},
    {"id": 10, "name": "Nick Vujicic"},
    {"id": 11, "name": "T. Harv Eker"},
    {"id": 12, "name": "Robin Sharma"},
    {"id": 13, "name": "George S. Clason"},
    {"id": 14, "name": "Stephen R. Covey"},
    {"id": 15, "name": "Nguyễn Nhật Ánh"},
    {"id": 16, "name": "Robert T. Kiyosaki"},
]

users = [
    {"id": 1, "name": "Quỳnh"},
    {"id": 2, "name": "Chiến"},
    {"id": 3, "name": "Đức"},
    {"id": 4, "name": "Khánh"}
]

borrowings = [
    {"user_id": 1, "book_id": 2, "borrow_date": "2025-10-10", "return_date": None},
    {"user_id": 2, "book_id": 8, "borrow_date": "2025-10-10", "return_date": None},
    {"user_id": 3, "book_id": 11, "borrow_date": "2025-10-10", "return_date": None},
    {"user_id": 4, "book_id": 15, "borrow_date": "2025-10-10", "return_date": None}
]

# ==========================
#   ROOT
# ==========================
@app.route('/')
def home():
    return jsonify({
        "message": "Library Management API",
        "resources": {
            "books": "/books",
            "authors": "/authors",
            "users": "/users",
            "borrowings": "/borrowings"
        }
    })

# ==========================
#   BOOKS CRUD
# ==========================
@app.route('/books', methods=['GET'])
def get_books():
    search = request.args.get('search', '').lower()
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 5))

    filtered = [b for b in books if search in b['title'].lower()]
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

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    before = len(books)
    books = [b for b in books if b['id'] != book_id]
    if len(books) == before:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": f"Book {book_id} deleted"})

# ==========================
#   AUTHORS CRUD
# ==========================
@app.route('/authors', methods=['GET'])
def get_authors():
    return jsonify(authors)

@app.route('/authors', methods=['POST'])
def add_author():
    data = request.get_json()
    new_id = max([a["id"] for a in authors]) + 1 if authors else 1
    new_author = {"id": new_id, "name": data.get("name")}
    authors.append(new_author)
    return jsonify(new_author), 201

@app.route('/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    data = request.get_json()
    author = next((a for a in authors if a['id'] == author_id), None)
    if not author:
        return jsonify({"error": "Author not found"}), 404
    author['name'] = data.get('name', author['name'])
    return jsonify(author)

@app.route('/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    global authors
    before = len(authors)
    authors = [a for a in authors if a['id'] != author_id]
    if len(authors) == before:
        return jsonify({"error": "Author not found"}), 404
    return jsonify({"message": f"Author {author_id} deleted"})

@app.route('/authors/<int:author_id>/books', methods=['GET'])
def get_books_by_author(author_id):
    author_books = [b for b in books if b['author_id'] == author_id]
    return jsonify(author_books)

# ==========================
#   USERS CRUD
# ==========================
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    new_id = max([u["id"] for u in users]) + 1 if users else 1
    new_user = {"id": new_id, "name": data.get("name")}
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user['name'] = data.get('name', user['name'])
    return jsonify(user)

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    before = len(users)
    users = [u for u in users if u['id'] != user_id]
    if len(users) == before:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": f"User {user_id} deleted"})

# ==========================
#   BORROW / RETURN
# ==========================
@app.route('/users/<int:user_id>/borrowings', methods=['GET'])
def get_user_borrowings(user_id):
    # Tìm user theo ID
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Lọc các bản ghi mượn theo user_id
    user_borrowings = [b for b in borrowings if b['user_id'] == user_id]

    # Lấy thông tin chi tiết từng sách
    borrowed_books = []
    for b in user_borrowings:
        book = next((bk for bk in books if bk['id'] == b['book_id']), None)
        if book:
            borrowed_books.append({
                "book_id": book['id'],
                "title": book['title'],
                "borrow_date": b['borrow_date'],
                "return_date": b['return_date']
            })

    return jsonify({
        "user": user['name'],
        "borrowed_books": borrowed_books
    })

@app.route('/users/<int:user_id>/borrowings', methods=['POST'])
def borrow_book(user_id):
    data = request.get_json()
    book_id = data.get('book_id')

    user = next((u for u in users if u['id'] == user_id), None)
    book = next((b for b in books if b['id'] == book_id), None)

    if not user or not book:
        return jsonify({"error": "Invalid user or book"}), 400
    if not book['available']:
        return jsonify({"error": "Book already borrowed"}), 400

    book['available'] = False
    borrowings.append({
        "user_id": user_id,
        "book_id": book_id,
        "borrow_date": datetime.now().strftime("%Y-%m-%d"),
        "return_date": None
    })
    return jsonify({"message": f"{user['name']} borrowed {book['title']}"})

@app.route('/users/<int:user_id>/return', methods=['POST'])
def return_book(user_id):
    data = request.get_json()
    book_id = data.get('book_id')

    record = next((b for b in borrowings if b['user_id'] == user_id and b['book_id'] == book_id and b['return_date'] is None), None)
    if not record:
        return jsonify({"error": "No active borrowing found"}), 400

    record['return_date'] = datetime.now().strftime("%Y-%m-%d")
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        book['available'] = True

    return jsonify({"message": "Book returned successfully", "record": record})

# ==========================
#   RUN SERVER
# ==========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

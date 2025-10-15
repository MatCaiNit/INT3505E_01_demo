from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==========================
#   DỮ LIỆU GIẢ LẬP
# ==========================
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
#   HÀM HỖ TRỢ TẠO LINK
# ==========================
def make_book_hateoas(book):
    return {
        **book,
        "_links": {
            "self": f"/books/{book['id']}",
            "author": f"/authors/{book['author_id']}",
            "borrow": f"/users/{{user_id}}/borrowings",
        }
    }

def make_author_hateoas(author):
    return {
        **author,
        "_links": {
            "self": f"/authors/{author['id']}",
            "books": f"/authors/{author['id']}/books"
        }
    }

def make_user_hateoas(user):
    return {
        **user,
        "_links": {
            "self": f"/users/{user['id']}",
            "borrowings": f"/users/{user['id']}/borrowings"
        }
    }

# ==========================
#   ROOT (ENTRY POINT)
# ==========================
@app.route('/')
def home():
    return jsonify({
        "message": "Library Management API",
        "_links": {
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
@app.route('/books', methods=['GET'])
def get_books():
    search = request.args.get('search', '').lower()
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 5))

    filtered = [b for b in books if search in b['title'].lower()]
    paginated = filtered[offset: offset + limit]

    data = {
        "total": len(filtered),
        "offset": offset,
        "limit": limit,
        "data": [make_book_hateoas(b) for b in paginated]
    }
    response = make_response(jsonify(data))
    response.headers["Cache-Control"] = "public, max-age=30"
    return response

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(make_book_hateoas(book))

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
    return jsonify(make_book_hateoas(new_book)), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    book['title'] = data.get('title', book['title'])
    book['author_id'] = data.get('author_id', book['author_id'])
    return jsonify(make_book_hateoas(book))

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
    return jsonify([make_author_hateoas(a) for a in authors])

@app.route('/authors/<int:author_id>/books', methods=['GET'])
def get_books_by_author(author_id):
    author_books = [b for b in books if b['author_id'] == author_id]
    return jsonify([make_book_hateoas(b) for b in author_books])

@app.route('/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    author = next((a for a in authors if a['id'] == author_id), None)
    if not author:
        return jsonify({"error": "Author not found"}), 404
    return jsonify(make_author_hateoas(author))


# ==========================
#   USERS + BORROWINGS
# ==========================
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify([make_user_hateoas(u) for u in users])

@app.route('/users/<int:user_id>/borrowings', methods=['GET'])
def get_user_borrowings(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_borrowings = [b for b in borrowings if b['user_id'] == user_id]
    borrowed_books = []
    for b in user_borrowings:
        book = next((bk for bk in books if bk['id'] == b['book_id']), None)
        if book:
            borrowed_books.append(make_book_hateoas(book))

    return jsonify({
        "user": make_user_hateoas(user),
        "borrowed_books": borrowed_books
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


if __name__ == '__main__':
    app.run(port=5000, debug=True)

from flask import Flask, jsonify, request
from flasgger import Swagger
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from functools import wraps # Thêm thư viện để tạo decorator

from flask_jwt_extended import (
    JWTManager, 
    create_access_token, 
    jwt_required, 
    create_refresh_token, 
    get_jwt_identity,
    set_refresh_cookies,
    unset_jwt_cookies,
    get_jwt, # Thêm để đọc claims (payload)
    verify_jwt_in_request # Thêm để xác thực token trong decorator
)

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "super-secret-key" # SỬA LỖI: "key" -> "KEY"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15) # Tăng thời gian AT lên 15 phút
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7) # Tăng thời gian RT lên 7 ngày
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False 
app.config["JWT_COOKIE_HTTPONLY"] = True 
app.config["JWT_COOKIE_CSRF_PROTECT"] = True 

jwt = JWTManager(app)

# Sử dụng path tuyệt đối để Flask luôn tìm được file
swagger_path = os.path.join(os.getcwd(), "openapi", "openapi.yaml")
swagger = Swagger(app, template_file=swagger_path)

# ==========================
#   DATABASE MOCK
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

# CẬP NHẬT: Thêm "role" (vai trò) vào cho user
users = [
    {"id": 1, "name": "Quynh", "role": "admin"},
    {"id": 2, "name": "Chiến", "role": "admin"},
    {"id": 3, "name": "Đức", "role": "user"},
    {"id": 4, "name": "Khánh", "role": "user"}
]

borrowings = [
    {"user_id": 1, "book_id": 2, "borrow_date": "2025-10-10", "return_date": None},
    {"user_id": 2, "book_id": 8, "borrow_date": "2025-10-10", "return_date": None},
    {"user_id": 3, "book_id": 11, "borrow_date": "2025-10-10", "return_date": None},
    {"user_id": 4, "book_id": 15, "borrow_date": "2025-10-10", "return_date": None}
]

# ==========================
#   CUSTOM DECORATOR (PHÂN QUYỀN)
# ==========================

# MỚI: Tạo một decorator tùy chỉnh để kiểm tra "role"
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # 1. Xác thực token (giống @jwt_required())
            verify_jwt_in_request()
            
            # 2. Lấy payload (claims) từ token
            claims = get_jwt()
            
            # 3. Kiểm tra xem "role" có phải là "admin" không
            if claims.get("role") == "admin":
                # 4. Nếu đúng, cho phép chạy hàm
                return fn(*args, **kwargs)
            else:
                # 5. Nếu không, trả về lỗi 403 Forbidden
                return jsonify({"error": "Admin access required"}), 403
        return decorator
    return wrapper

# ==========================
#   AUTHENTICATION (XÁC THỰC)
# ==========================

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("name")
    user = next((u for u in users if u["name"].lower() == username.lower()), None)
    
    if not user:
        return jsonify({"error": "Invalid user"}), 401

    # CẬP NHẬT: Thêm "role" vào JWT payload (claims)
    # "identity" là định danh chính, "additional_claims" là thông tin bổ sung
    access_token = create_access_token(
        identity=str(user["id"]), 
        additional_claims={"role": user["role"]}
    )
    
    # Refresh token không cần chứa role, chỉ cần identity
    refresh_token = create_refresh_token(identity=str(user["id"]))
    
    response_body = {
        "message": "Login successful",
        "access_token": access_token 
    }
    response = jsonify(response_body)
    set_refresh_cookies(response, refresh_token)
    return response, 200

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    
    # Khi refresh, chúng ta cũng cần lấy lại role từ database (hoặc từ chính refresh token nếu muốn)
    # Ở đây, ta lấy lại từ "database" users
    user = next((u for u in users if u['id'] == int(current_user_id)), None)
    role = user.get("role", "user") if user else "user"

    # CẬP NHẬT: Tạo AT mới cũng phải chứa role
    new_access_token = create_access_token(
        identity=current_user_id,
        additional_claims={"role": role}
    )
    
    return jsonify({
        "message": "Access token refreshed",
        "access_token": new_access_token
    }), 200

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response) 
    return response, 200

# ==========================
#   HOME
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
#   BOOKS CRUD
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
@jwt_required() # Bất kỳ user nào đăng nhập cũng có thể thêm sách
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
@jwt_required() # Bất kỳ user nào đăng nhập cũng có thể sửa sách
def update_book(book_id):
    data = request.get_json()
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    book['title'] = data.get('title', book['title'])
    book['author_id'] = data.get('author_id', book['author_id'])
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
@admin_required() # CẬP NHẬT: Chỉ admin mới được phép xóa sách
def delete_book(book_id):
    global books
    before = len(books)
    books = [b for b in books if b['id'] != book_id]
    if len(books) == before:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": f"Book {book_id} deleted"})

# ==========================
#   AUTHORS CRUD
# ==========================
@app.route('/authors', methods=['GET'])
def get_authors():
    return jsonify(authors)

@app.route('/authors', methods=['POST'])
@admin_required() # CẬP NHẬT: Chỉ admin mới được thêm tác giả
def add_author():
    data = request.get_json()
    new_id = max([a["id"] for a in authors]) + 1 if authors else 1
    new_author = {"id": new_id, "name": data.get("name")}
    authors.append(new_author)
    return jsonify(new_author), 201

@app.route('/authors/<int:author_id>', methods=['PUT'])
@admin_required() # CẬP NHẬT: Chỉ admin mới được sửa tác giả
def update_author(author_id):
    data = request.get_json()
    author = next((a for a in authors if a['id'] == author_id), None)
    if not author:
        return jsonify({"error": "Author not found"}), 404
    author['name'] = data.get('name', author['name'])
    return jsonify(author)

@app.route('/authors/<int:author_id>', methods=['DELETE'])
@admin_required() # CẬP NHẬT: Chỉ admin mới được xóa tác giả
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
#   USERS (Chỉ admin mới được quản lý user)
# ==========================
@app.route('/users', methods=['GET'])
@admin_required()
def get_users():
    return jsonify(users)

@app.route('/users', methods=['POST'])
@admin_required()
def add_user():
    data = request.get_json()
    new_id = max([u["id"] for u in users]) + 1 if users else 1
    new_user = {
        "id": new_id, 
        "name": data.get("name"),
        "role": data.get("role", "user") # Cho phép gán role khi tạo
    }
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/users/<int:user_id>', methods=['GET'])
@admin_required() # Chỉ admin mới được xem thông tin user khác
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)

@app.route('/users/<int:user_id>', methods=['PUT'])
@admin_required()
def update_user(user_id):
    data = request.get_json()
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user['name'] = data.get('name', user['name'])
    user['role'] = data.get('role', user['role']) # Cho phép admin đổi role
    return jsonify(user)

@app.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required()
def delete_user(user_id):
    global users
    # Ngăn admin tự xóa mình
    current_user_id = get_jwt_identity()
    if str(user_id) == current_user_id:
        return jsonify({"error": "Admin cannot delete themselves"}), 400
        
    before = len(users)
    users = [u for u in users if u['id'] != user_id]
    if len(users) == before:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"message": f"User {user_id} deleted"})

# ==========================
#   BORROWINGS (Logic mượn/trả sách)
# ==========================

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
@jwt_required() # Bất kỳ user nào đăng nhập cũng có thể mượn sách
def borrow_book(user_id):
    # Kiểm tra xem user có mượn sách cho chính mình không
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if str(user_id) != current_user_id and claims.get("role") != "admin":
        return jsonify({"error": "Users can only borrow books for themselves"}), 403

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

@app.route('/users/<int:user_id>/returnings', methods=['POST'])
@jwt_required() # Bất kỳ user nào đăng nhập cũng có thể trả sách
def return_book(user_id):
    # Kiểm tra xem user có trả sách cho chính mình không
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if str(user_id) != current_user_id and claims.get("role") != "admin":
        return jsonify({"error": "Users can only return books for themselves"}), 403
        
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


if __name__ == '__main__':
    # Tạo thư mục openapi nếu chưa tồn tại
    if not os.path.exists('openapi'):
        os.makedirs('openapi')
    app.run(host='0.0.0.0', port=5000, debug=True)


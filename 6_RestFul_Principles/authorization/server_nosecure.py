from flask import Flask, jsonify, request
from flasgger import Swagger
from flask_cors import CORS
import os
from datetime import datetime, timedelta

from flask_jwt_extended import (
    JWTManager, 
    create_access_token, 
    jwt_required, 
    create_refresh_token,  
    get_jwt_identity
)

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "a-very-weak-and-predictable-key"


app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=5) 
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)


app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_COOKIE_HTTPONLY"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

jwt = JWTManager(app)


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
    {"id": 1, "name": "Quynh"},
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



@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("name")
    user = next((u for u in users if u["name"].lower() == username.lower()), None)
    if not user:
        return jsonify({"error": "Invalid user"}), 401

    identity = str(user["id"])
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    

    return jsonify({
        "message": "Login successful (INSECURE)",
        "access_token": access_token,
        "refresh_token": refresh_token 
    }), 200

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True) # Yêu cầu refresh token
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        "message": "Access token refreshed (by hacker?)",
        "access_token": new_access_token
    }), 200



@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)

@app.route('/books', methods=['POST'])
@jwt_required() # Yêu cầu Access Token
def add_book():
    data = request.get_json()
    new_id = max([b["id"] for b in books]) + 1 if books else 1
    new_book = { "id": new_id, "title": data.get("title"), "author_id": data.get("author_id"), "available": True }
    books.append(new_book)
    return jsonify(new_book), 201



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, jsonify, request
from flasgger import Swagger
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from functools import wraps # Cần thiết để tạo decorator

from flask_jwt_extended import (
    JWTManager, 
    create_access_token, 
    jwt_required, 
    get_jwt, # Để đọc JTI
    get_jwt_identity
)

app = Flask(__name__)
CORS(app)

# --- CẤU HÌNH JWT (Tập trung vào JTI) ---
app.config["JWT_SECRET_KEY"] = "super-secret-key-jti-demo"
# Token sống 60 giây để test
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=60)
# Tự động thêm claim "jti" (JWT ID) vào mỗi Access Token
app.config["JWT_JTI_CLAIM"] = "jti" 

jwt = JWTManager(app)


JTI_BLACKLIST = set()   

books = []
users = [ {"id": 1, "name": "Quynh"} ]

def replay_protection_required(fn):
    @wraps(fn)
    @jwt_required() # Phải đăng nhập trước
    def wrapper(*args, **kwargs):
        # Lấy payload của token (đã được xác thực)
        jwt_payload = get_jwt()
        # Lấy jti (JWT ID) từ payload
        jti = jwt_payload["jti"]
        # Kiểm tra xem jti này đã có trong blacklist chưa
        if jti in JTI_BLACKLIST:
            # Nếu CÓ -> Đây là Replay Attack!
            return jsonify(
                message="Replay attack detected! Token has already been used."
            ), 401
        # Nếu CHƯA -> Thêm jti vào blacklist
        JTI_BLACKLIST.add(jti)
        # In ra terminal để chúng ta thấy
        print(f"JTI {jti} đã được sử dụng và thêm vào blacklist.")
        # Cho phép chạy hàm API gốc (vd: add_book)
        return fn(*args, **kwargs)
    return wrapper
# ----------------------------------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("name")
    user = next((u for u in users if u["name"].lower() == username.lower()), None)
    if not user:
        return jsonify({"error": "Invalid user"}), 401

    access_token = create_access_token(identity=str(user["id"]))
    return jsonify({
        "message": "Login successful",
        "access_token": access_token 
    })

@app.route('/books', methods=['POST'])
@replay_protection_required
def add_book():
    """
    Endpoint nhạy cảm, chỉ được dùng token 1 LẦN.
    """
    data = request.get_json()
    new_id = len(books) + 1
    new_book = { "id": new_id, "title": data.get("title") }
    books.append(new_book)
    return jsonify(new_book), 201

@app.route('/check-blacklist', methods=['GET'])
def check_blacklist():
    return jsonify(list(JTI_BLACKLIST))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


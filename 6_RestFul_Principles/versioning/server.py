from flask import Flask, jsonify, request
from flasgger import Swagger
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from api_v1 import api_v1
from api_v2 import api_v2
from data import users
from flask_jwt_extended import JWTManager, create_access_token, jwt_required


app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "super-secret-key"  # nên để trong biến môi trường
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# Sử dụng path tuyệt đối để Flask luôn tìm được file
swagger_path = os.path.join(os.getcwd(), "openapi", "openapi.yaml")
swagger = Swagger(app, template_file=swagger_path)

app.register_blueprint(api_v1, url_prefix='/api/v1')

app.register_blueprint(api_v2, url_prefix='/api/v2')


@app.route('/')
def index():
    """Trang chủ hiển thị các phiên bản API."""
    return jsonify({
        "message": "Welcome to the Versioned Book API!",
        "api_versions": {
            "v1": "Access API v1 at /api/v1/books",
            "v2": "Access API v2 at /api/v2/books"
        },
        "documentation": "Access Swagger UI at /apidocs"
    })

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Missing name in request body"}), 400
        
    username_from_request = data.get("name")

    user = next((u for u in users if u["name"].lower() == username_from_request.lower()), None)
    
    if not user:
        return jsonify({"error": "Invalid user"}), 401

    access_token = create_access_token(identity=str(user["id"]))
    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

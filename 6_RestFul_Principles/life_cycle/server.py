from flask import Flask, jsonify, request, make_response
from flasgger import Swagger
from flask_cors import CORS
import os
from datetime import datetime, timedelta
from functools import wraps
import math

from flask_jwt_extended import (
    JWTManager, 
    create_access_token, 
    jwt_required, 
    create_refresh_token, 
    get_jwt_identity,
    set_refresh_cookies,
    unset_jwt_cookies,
    get_jwt,
    verify_jwt_in_request
)

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False 
app.config["JWT_COOKIE_HTTPONLY"] = True 
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Set to False for easier testing

jwt = JWTManager(app)

swagger_path = os.path.join(os.getcwd(), "openapi", "openapi.yaml")
swagger = Swagger(app, template_file=swagger_path)

# ==========================================
# DATA STORAGE
# ==========================================

books = [
    {"id": 1, "title": "Clean Code", "author_id": 1, "available": True, "published_year": 2008},
    {"id": 2, "title": "The Pragmatic Programmer", "author_id": 2, "available": False, "published_year": 1999},
    {"id": 3, "title": "Refactoring", "author_id": 3, "available": True, "published_year": 1999},
    {"id": 4, "title": "Design Patterns", "author_id": 4, "available": True, "published_year": 1994},
    {"id": 5, "title": "Python Crash Course", "author_id": 5, "available": True, "published_year": 2015},
    {"id": 6, "title": "Đắc Nhân Tâm", "author_id": 6, "available": True, "published_year": 1936},
    {"id": 7, "title": "Sự im lặng của bầy cừu", "author_id": 7, "available": True, "published_year": 1988},
    {"id": 8, "title": "Tuổi trẻ đáng giá bao nhiêu", "author_id": 8, "available": False, "published_year": 2017},
]

authors = [
    {"id": 1, "name": "Robert C. Martin", "bio": "Software engineer and author of Clean Code"},
    {"id": 2, "name": "Andrew Hunt", "bio": "Co-author of The Pragmatic Programmer"},
    {"id": 3, "name": "Martin Fowler", "bio": "Chief Scientist at ThoughtWorks"},
    {"id": 4, "name": "Erich Gamma", "bio": "Software engineer, co-author of Design Patterns"},
    {"id": 5, "name": "Eric Matthes", "bio": "High school teacher and programmer"},
    {"id": 6, "name": "Dale Carnegie", "bio": "American writer and lecturer"},
    {"id": 7, "name": "Thomas Harris", "bio": "American writer, author of psychological thrillers"},
    {"id": 8, "name": "Rosie Nguyễn", "bio": "Vietnamese author and entrepreneur"},
]

users = [
    {"id": 1, "name": "Quynh", "role": "admin", "email": "quynh@library.com", 
     "created_at": "2025-01-01T10:00:00Z", "last_login": "2025-11-26T09:30:00Z"},
    {"id": 2, "name": "Chiến", "role": "admin", "email": "chien@library.com",
     "created_at": "2025-01-05T14:20:00Z", "last_login": "2025-11-25T16:45:00Z"},
    {"id": 3, "name": "Đức", "role": "user", "email": "duc@library.com",
     "created_at": "2025-02-10T08:15:00Z", "last_login": "2025-11-24T11:20:00Z"},
    {"id": 4, "name": "Khánh", "role": "user", "email": "khanh@library.com",
     "created_at": "2025-03-15T13:45:00Z", "last_login": "2025-11-20T15:10:00Z"}
]

borrowings = [
    {"id": 1, "user_id": 1, "book_id": 2, "borrow_date": "2025-11-10", "return_date": None, "days_borrowed": 16},
    {"id": 2, "user_id": 2, "book_id": 8, "borrow_date": "2025-11-15", "return_date": None, "days_borrowed": 11},
    {"id": 3, "user_id": 3, "book_id": 4, "borrow_date": "2025-10-20", "return_date": "2025-11-05", "days_borrowed": 16},
    {"id": 4, "user_id": 4, "book_id": 6, "borrow_date": "2025-10-25", "return_date": "2025-11-10", "days_borrowed": 16},
]

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def add_deprecation_headers(response):
    """Add deprecation headers to v1 responses"""
    response.headers['Deprecation'] = 'Sun, 01 Dec 2025 00:00:00 GMT'
    response.headers['Sunset'] = 'Sun, 01 Jun 2026 00:00:00 GMT'
    response.headers['Link'] = '<https://docs.library.com/migration>; rel="deprecation"'
    response.headers['Warning'] = '299 - "API v1 is deprecated. Please migrate to v2."'
    return response

def get_author_by_id(author_id):
    return next((a for a in authors if a['id'] == author_id), None)

def get_user_by_id(user_id):
    return next((u for u in users if u['id'] == user_id), None)

def get_book_by_id(book_id):
    return next((b for b in books if b['id'] == book_id), None)

def format_book_v2(book):
    """Format book data for v2 with nested author"""
    author = get_author_by_id(book['author_id'])
    return {
        "id": book['id'],
        "title": book['title'],
        "author": {
            "id": author['id'],
            "name": author['name'],
            "bio": author.get('bio', '')
        } if author else None,
        "published_year": book.get('published_year'),
        "available": book['available'],
        "created_at": "2025-01-15T10:30:00Z",
        "updated_at": "2025-11-20T14:25:00Z"
    }

def format_author_v1(author):
    """Format author for v1 - basic info only"""
    return {
        "id": author['id'],
        "name": author['name']
    }

def format_author_v2(author):
    """Format author for v2 - with bio and book count"""
    book_count = len([b for b in books if b['author_id'] == author['id']])
    return {
        "id": author['id'],
        "name": author['name'],
        "bio": author.get('bio', ''),
        "book_count": book_count
    }

def format_user_v1(user):
    """Format user for v1 - basic info only"""
    return {
        "id": user['id'],
        "name": user['name'],
        "role": user['role']
    }

def format_user_v2(user):
    """Format user for v2 - with additional details"""
    return {
        "id": user['id'],
        "name": user['name'],
        "role": user['role'],
        "email": user.get('email', ''),
        "created_at": user.get('created_at', ''),
        "last_login": user.get('last_login', '')
    }

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") == "admin":
                return fn(*args, **kwargs)
            else:
                return jsonify({"error": "Admin access required"}), 403
        return decorator
    return wrapper

# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("name")
    user = next((u for u in users if u["name"].lower() == username.lower()), None)
    
    if not user:
        return jsonify({"error": "Invalid user"}), 401

    access_token = create_access_token(
        identity=str(user["id"]), 
        additional_claims={"role": user["role"]}
    )
    
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
    user = get_user_by_id(int(current_user_id))
    role = user.get("role", "user") if user else "user"
    
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

# ==========================================
# STRATEGY 1: URL VERSIONING (BOOKS)
# ==========================================

@app.route('/api/v1/books', methods=['GET'])
def get_books_v1():
    """V1: Deprecated - uses offset/limit pagination"""
    search = request.args.get('search', '').lower()
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 5))

    filtered = [b for b in books if search in b['title'].lower()]
    paginated = filtered[offset: offset + limit]

    response = jsonify({
        "total": len(filtered),
        "offset": offset,
        "limit": limit,
        "data": paginated
    })
    
    return add_deprecation_headers(response)

@app.route('/api/v2/books', methods=['GET'])
def get_books_v2():
    """V2: Current - uses page/per_page pagination with nested author"""
    search = request.args.get('search', '').lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
    
    filtered = [b for b in books if search in b['title'].lower()]
    
    total_items = len(filtered)
    total_pages = math.ceil(total_items / per_page) if per_page > 0 else 0
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated = filtered[start_idx:end_idx]
    
    data = [format_book_v2(b) for b in paginated]
    
    return jsonify({
        "data": data,
        "meta": {
            "current_page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages
        }
    })

# ==========================================
# STRATEGY 2: HEADER VERSIONING (AUTHORS)
# ==========================================

@app.route('/api/authors', methods=['GET'])
def get_authors():
    """Authors endpoint - version controlled by API-Version header"""
    api_version = request.headers.get('API-Version', '2')
    
    if api_version == '1':
        # V1: Return simple list with basic info
        data = [format_author_v1(a) for a in authors]
        response = make_response(jsonify(data))
        response.headers['API-Version'] = '1'
        return response
    else:
        # V2: Return detailed list with meta
        data = [format_author_v2(a) for a in authors]
        response = make_response(jsonify({
            "data": data,
            "meta": {
                "total": len(authors),
                "version": "2"
            }
        }))
        response.headers['API-Version'] = '2'
        return response

@app.route('/api/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """Get author detail - version controlled by API-Version header"""
    api_version = request.headers.get('API-Version', '2')
    author = get_author_by_id(author_id)
    
    if not author:
        return jsonify({"error": "Author not found"}), 404
    
    if api_version == '1':
        response = make_response(jsonify({"data": format_author_v1(author)}))
        response.headers['API-Version'] = '1'
        return response
    else:
        response = make_response(jsonify({"data": format_author_v2(author)}))
        response.headers['API-Version'] = '2'
        return response

@app.route('/api/authors', methods=['POST'])
@jwt_required()
def add_author():
    """Add author - version controlled by API-Version header"""
    api_version = request.headers.get('API-Version', '2')
    data = request.get_json()
    
    if not data.get("name"):
        return jsonify({"error": "name is required"}), 400
    
    new_id = max([a["id"] for a in authors]) + 1 if authors else 1
    new_author = {
        "id": new_id,
        "name": data.get("name"),
        "bio": data.get("bio", "") if api_version == '2' else ""
    }
    authors.append(new_author)
    
    if api_version == '1':
        response = make_response(jsonify({
            "data": format_author_v1(new_author),
            "message": "Author created successfully"
        }), 201)
        response.headers['API-Version'] = '1'
        return response
    else:
        response = make_response(jsonify({
            "data": format_author_v2(new_author),
            "message": "Author created successfully"
        }), 201)
        response.headers['API-Version'] = '2'
        return response

@app.route('/api/authors/<int:author_id>', methods=['PUT'])
@jwt_required()
def update_author(author_id):
    """Update author - version controlled by API-Version header"""
    api_version = request.headers.get('API-Version', '2')
    data = request.get_json()
    author = get_author_by_id(author_id)
    
    if not author:
        return jsonify({"error": "Author not found"}), 404
    
    if data.get("name"):
        author['name'] = data.get('name')
    if api_version == '2' and data.get("bio") is not None:
        author['bio'] = data.get('bio')
    
    if api_version == '1':
        response = make_response(jsonify({"data": format_author_v1(author)}))
        response.headers['API-Version'] = '1'
        return response
    else:
        response = make_response(jsonify({"data": format_author_v2(author)}))
        response.headers['API-Version'] = '2'
        return response

# ==========================================
# STRATEGY 3: QUERY PARAMETER VERSIONING (USERS)
# ==========================================

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    """Users endpoint - version controlled by ?version query parameter"""
    version = int(request.args.get('version', 2))
    
    if version == 1:
        # V1: Simple list with basic info
        data = [format_user_v1(u) for u in users]
        return jsonify(data)
    else:
        # V2: Detailed list with meta
        data = [format_user_v2(u) for u in users]
        active_users = len([u for u in users if u.get('last_login')])
        return jsonify({
            "data": data,
            "meta": {
                "total": len(users),
                "active_users": active_users
            }
        })

@app.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user detail - version controlled by ?version query parameter"""
    version = int(request.args.get('version', 2))
    user = get_user_by_id(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if version == 1:
        return jsonify({"data": format_user_v1(user)})
    else:
        return jsonify({"data": format_user_v2(user)})

# ==========================================
# STRATEGY 4: CONTENT NEGOTIATION (REPORTS)
# ==========================================

@app.route('/api/reports/borrowings', methods=['GET'])
@jwt_required()
def get_borrowing_report():
    """Borrowing report - version controlled by Accept header"""
    accept_header = request.headers.get('Accept', 'application/vnd.library.v2+json')
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Filter borrowings by date if provided
    filtered_borrowings = borrowings
    
    if 'v1' in accept_header or accept_header == 'application/vnd.library.v1+json':
        # V1: Basic report
        active = len([b for b in filtered_borrowings if b['return_date'] is None])
        
        report = {
            "total_borrowings": len(filtered_borrowings),
            "active_borrowings": active,
            "borrowings": [
                {
                    "user_name": get_user_by_id(b['user_id'])['name'],
                    "book_title": get_book_by_id(b['book_id'])['title'],
                    "borrow_date": b['borrow_date']
                }
                for b in filtered_borrowings
            ]
        }
        
        response = make_response(jsonify(report))
        response.headers['Content-Type'] = 'application/vnd.library.v1+json'
        return response
    
    else:
        # V2: Detailed report with analytics
        active = [b for b in filtered_borrowings if b['return_date'] is None]
        returned = [b for b in filtered_borrowings if b['return_date'] is not None]
        
        # Calculate analytics
        avg_days = sum(b['days_borrowed'] for b in filtered_borrowings) / len(filtered_borrowings) if filtered_borrowings else 0
        
        # Most borrowed books
        book_counts = {}
        for b in filtered_borrowings:
            book_counts[b['book_id']] = book_counts.get(b['book_id'], 0) + 1
        
        most_borrowed = sorted(book_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        most_borrowed_books = [
            {
                "book": format_book_v2(get_book_by_id(book_id)),
                "borrow_count": count
            }
            for book_id, count in most_borrowed
        ]
        
        # Most active users
        user_counts = {}
        for b in filtered_borrowings:
            user_counts[b['user_id']] = user_counts.get(b['user_id'], 0) + 1
        
        most_active = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        most_active_users = [
            {
                "user": format_user_v2(get_user_by_id(user_id)),
                "borrow_count": count
            }
            for user_id, count in most_active
        ]
        
        report = {
            "summary": {
                "total_borrowings": len(filtered_borrowings),
                "active_borrowings": len(active),
                "returned_borrowings": len(returned),
                "average_borrow_days": round(avg_days, 2)
            },
            "analytics": {
                "most_borrowed_books": most_borrowed_books,
                "most_active_users": most_active_users
            },
            "borrowings": [
                {
                    "id": b['id'],
                    "user": format_user_v2(get_user_by_id(b['user_id'])),
                    "book": format_book_v2(get_book_by_id(b['book_id'])),
                    "borrow_date": b['borrow_date'],
                    "return_date": b['return_date'],
                    "days_borrowed": b['days_borrowed']
                }
                for b in filtered_borrowings
            ]
        }
        
        response = make_response(jsonify(report))
        response.headers['Content-Type'] = 'application/vnd.library.v2+json'
        return response

@app.route('/api/reports/books', methods=['GET'])
@jwt_required()
def get_book_report():
    """Book report - version controlled by Accept header"""
    accept_header = request.headers.get('Accept', 'application/vnd.library.v2+json')
    
    if 'v1' in accept_header or accept_header == 'application/vnd.library.v1+json':
        # V1: Basic stats
        available = len([b for b in books if b['available']])
        
        report = {
            "total_books": len(books),
            "available_books": available
        }
        
        response = make_response(jsonify(report))
        response.headers['Content-Type'] = 'application/vnd.library.v1+json'
        return response
    
    else:
        # V2: Detailed stats with breakdowns
        available = len([b for b in books if b['available']])
        borrowed = len(books) - available
        availability_rate = (available / len(books) * 100) if books else 0
        
        # By author
        author_counts = {}
        for b in books:
            author_counts[b['author_id']] = author_counts.get(b['author_id'], 0) + 1
        
        by_author = [
            {
                "author": format_author_v2(get_author_by_id(author_id)),
                "book_count": count
            }
            for author_id, count in author_counts.items()
        ]
        
        # By year
        year_counts = {}
        for b in books:
            year = b.get('published_year', 'Unknown')
            year_counts[year] = year_counts.get(year, 0) + 1
        
        by_year = [
            {
                "year": year,
                "book_count": count
            }
            for year, count in sorted(year_counts.items())
        ]
        
        report = {
            "summary": {
                "total_books": len(books),
                "available_books": available,
                "borrowed_books": borrowed,
                "availability_rate": round(availability_rate, 2)
            },
            "by_author": by_author,
            "by_year": by_year
        }
        
        response = make_response(jsonify(report))
        response.headers['Content-Type'] = 'application/vnd.library.v2+json'
        return response

# ==========================================
# BORROWING OPERATIONS
# ==========================================

@app.route('/users/<int:user_id>/borrowings', methods=['GET'])
def get_user_borrowings(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user_borrowings = [b for b in borrowings if b['user_id'] == user_id]
    borrowed_books = []
    
    for b in user_borrowings:
        book = get_book_by_id(b['book_id'])
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
@jwt_required()
def borrow_book(user_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if str(user_id) != current_user_id and claims.get("role") != "admin":
        return jsonify({"error": "Users can only borrow books for themselves"}), 403

    data = request.get_json()
    book_id = data.get('book_id')

    user = get_user_by_id(user_id)
    book = get_book_by_id(book_id)

    if not user or not book:
        return jsonify({"error": "Invalid user or book"}), 400
    if not book['available']:
        return jsonify({"error": "Book already borrowed"}), 400

    book['available'] = False
    new_id = max([b['id'] for b in borrowings]) + 1 if borrowings else 1
    borrowings.append({
        "id": new_id,
        "user_id": user_id,
        "book_id": book_id,
        "borrow_date": datetime.now().strftime("%Y-%m-%d"),
        "return_date": None,
        "days_borrowed": 0
    })
    
    return jsonify({"message": f"{user['name']} borrowed {book['title']}"})

@app.route('/users/<int:user_id>/returnings', methods=['POST'])
@jwt_required()
def return_book(user_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if str(user_id) != current_user_id and claims.get("role") != "admin":
        return jsonify({"error": "Users can only return books for themselves"}), 403
        
    data = request.get_json()
    book_id = data.get('book_id')

    record = next((b for b in borrowings if b['user_id'] == user_id and 
                   b['book_id'] == book_id and b['return_date'] is None), None)
    if not record:
        return jsonify({"error": "No active borrowing found"}), 400

    record['return_date'] = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate days borrowed
    borrow_date = datetime.strptime(record['borrow_date'], "%Y-%m-%d")
    return_date = datetime.strptime(record['return_date'], "%Y-%m-%d")
    record['days_borrowed'] = (return_date - borrow_date).days
    
    book = get_book_by_id(book_id)
    if book:
        book['available'] = True

    return jsonify({"message": "Book returned successfully", "record": record})

# ==========================================
# HOME
# ==========================================

@app.route('/')
def home():
    return jsonify({
        "message": "Library Management API - Multi-Strategy Versioning",
        "versioning_strategies": {
            "books": {
                "strategy": "URL Versioning",
                "v1": "/api/v1/books (deprecated)",
                "v2": "/api/v2/books (current)",
                "differences": "v1 uses offset/limit, v2 uses page/per_page with nested author"
            },
            "authors": {
                "strategy": "Header Versioning",
                "endpoint": "/api/authors",
                "header": "API-Version: 1 or 2",
                "differences": "v1 basic info, v2 includes bio and book_count"
            },
            "users": {
                "strategy": "Query Parameter Versioning",
                "endpoint": "/api/users",
                "parameter": "?version=1 or ?version=2",
                "differences": "v1 basic info, v2 includes email, timestamps"
            },
            "reports": {
                "strategy": "Content Negotiation",
                "endpoint": "/api/reports/*",
                "header": "Accept: application/vnd.library.v1+json or v2+json",
                "differences": "v1 basic stats, v2 detailed analytics"
            }
        },
        "docs": "/apidocs"
    })

if __name__ == '__main__':
    if not os.path.exists('openapi'):
        os.makedirs('openapi')
    app.run(host='0.0.0.0', port=5000, debug=True)
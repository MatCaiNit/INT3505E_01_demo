from flask import Flask, jsonify, request, make_response
from flasgger import Swagger
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from datetime import datetime, timedelta
from functools import wraps
import math
import logging
import time
import uuid
from collections import defaultdict

# Prometheus metrics
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge, generate_latest

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

# ==========================================
# LOGGING CONFIGURATION
# ==========================================

# Create logs directory
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

# Create separate loggers
app_logger = logging.getLogger('app')
security_logger = logging.getLogger('security')
audit_logger = logging.getLogger('audit')

# File handlers for different log types
security_handler = logging.FileHandler('logs/security.log')
security_handler.setFormatter(logging.Formatter(
    '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
))
security_logger.addHandler(security_handler)

audit_handler = logging.FileHandler('logs/audit.log')
audit_handler.setFormatter(logging.Formatter(
    '%(asctime)s - AUDIT - %(message)s'
))
audit_logger.addHandler(audit_handler)

# ==========================================
# FLASK APP INITIALIZATION
# ==========================================

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = os.getenv("FLASK_ENV") == "production"
app.config["JWT_COOKIE_HTTPONLY"] = True 
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

jwt = JWTManager(app)

# ==========================================
# RATE LIMITING CONFIGURATION
# ==========================================

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Custom rate limit handler
@app.errorhandler(429)
def ratelimit_handler(e):
    security_logger.warning(f"Rate limit exceeded for IP: {get_remote_address()}")
    return jsonify({
        "error": "Rate limit exceeded",
        "message": str(e.description)
    }), 429

# ==========================================
# PROMETHEUS METRICS
# ==========================================

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Custom metrics
request_counter = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_latency = Histogram(
    'api_request_duration_seconds',
    'API request latency',
    ['method', 'endpoint']
)

active_users = Gauge(
    'active_users_total',
    'Number of active users'
)

books_available = Gauge(
    'books_available_total',
    'Number of available books'
)

failed_auth_counter = Counter(
    'failed_auth_attempts_total',
    'Total failed authentication attempts',
    ['reason']
)

# ==========================================
# CIRCUIT BREAKER IMPLEMENTATION
# ==========================================

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = defaultdict(int)
        self.last_failure_time = defaultdict(float)
        self.state = defaultdict(lambda: "closed")  # closed, open, half_open
    
    def call(self, service_name, func, *args, **kwargs):
        current_state = self.state[service_name]
        
        # If circuit is open, check if timeout has passed
        if current_state == "open":
            if time.time() - self.last_failure_time[service_name] > self.timeout:
                self.state[service_name] = "half_open"
                app_logger.info(f"Circuit breaker for {service_name} is now HALF_OPEN")
            else:
                raise Exception(f"Circuit breaker is OPEN for {service_name}")
        
        try:
            result = func(*args, **kwargs)
            
            # Reset on success
            if current_state == "half_open":
                self.state[service_name] = "closed"
                self.failures[service_name] = 0
                app_logger.info(f"Circuit breaker for {service_name} is now CLOSED")
            
            return result
            
        except Exception as e:
            self.failures[service_name] += 1
            self.last_failure_time[service_name] = time.time()
            
            if self.failures[service_name] >= self.failure_threshold:
                self.state[service_name] = "open"
                app_logger.error(f"Circuit breaker OPENED for {service_name}")
            
            raise e

circuit_breaker = CircuitBreaker()

# ==========================================
# MIDDLEWARE FOR REQUEST TRACKING
# ==========================================

@app.before_request
def before_request():
    # Generate request ID for tracing
    request.id = str(uuid.uuid4())
    request.start_time = time.time()
    
    # Log incoming request
    app_logger.info(
        f"REQUEST_ID={request.id} | "
        f"METHOD={request.method} | "
        f"PATH={request.path} | "
        f"IP={get_remote_address()} | "
        f"USER_AGENT={request.headers.get('User-Agent', 'Unknown')}"
    )

@app.after_request
def after_request(response):
    # Calculate request duration
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        
        # Update metrics
        request_counter.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
        
        request_latency.labels(
            method=request.method,
            endpoint=request.path
        ).observe(duration)
        
        # Log response
        app_logger.info(
            f"RESPONSE_ID={getattr(request, 'id', 'unknown')} | "
            f"STATUS={response.status_code} | "
            f"DURATION={duration:.3f}s"
        )
    
    # Add custom headers
    response.headers['X-Request-ID'] = getattr(request, 'id', 'unknown')
    response.headers['X-Response-Time'] = f"{duration:.3f}s" if hasattr(request, 'start_time') else '0s'
    
    return response

# ==========================================
# SWAGGER CONFIGURATION
# ==========================================

swagger_path = os.path.join(os.getcwd(), "openapi", "openapi.yaml")
if os.path.exists(swagger_path):
    swagger = Swagger(app, template_file=swagger_path)
else:
    swagger = Swagger(app)

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

def update_metrics():
    """Update Gauge metrics"""
    books_available.set(len([b for b in books if b['available']]))
    active_users.set(len([u for u in users if u.get('last_login')]))

def audit_log(action, user_id, details):
    """Log audit trail"""
    audit_logger.info(
        f"USER_ID={user_id} | "
        f"ACTION={action} | "
        f"DETAILS={details} | "
        f"IP={get_remote_address()}"
    )

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

def format_author_v2(author):
    """Format author for v2 - with bio and book count"""
    book_count = len([b for b in books if b['author_id'] == author['id']])
    return {
        "id": author['id'],
        "name": author['name'],
        "bio": author.get('bio', ''),
        "book_count": book_count
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
            user_id = get_jwt_identity()
            
            if claims.get("role") != "admin":
                security_logger.warning(
                    f"Unauthorized admin access attempt by user_id={user_id} "
                    f"to {request.path}"
                )
                return jsonify({"error": "Admin access required"}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")  # Stricter rate limit for login
def login():
    data = request.get_json()
    username = data.get("name")
    
    if not username:
        failed_auth_counter.labels(reason="missing_username").inc()
        security_logger.warning(f"Login attempt with missing username from IP: {get_remote_address()}")
        return jsonify({"error": "Username is required"}), 400
    
    user = next((u for u in users if u["name"].lower() == username.lower()), None)
    
    if not user:
        failed_auth_counter.labels(reason="invalid_user").inc()
        security_logger.warning(f"Failed login attempt for username: {username} from IP: {get_remote_address()}")
        return jsonify({"error": "Invalid user"}), 401

    access_token = create_access_token(
        identity=str(user["id"]), 
        additional_claims={"role": user["role"]}
    )
    
    refresh_token = create_refresh_token(identity=str(user["id"]))
    
    # Update last login
    user['last_login'] = datetime.now().isoformat() + 'Z'
    update_metrics()
    
    # Audit log
    audit_log("LOGIN", user["id"], f"User {username} logged in successfully")
    
    security_logger.info(f"Successful login for user_id={user['id']} from IP: {get_remote_address()}")
    
    response_body = {
        "message": "Login successful",
        "access_token": access_token,
        "user": format_user_v2(user)
    }
    response = jsonify(response_body)
    set_refresh_cookies(response, refresh_token)
    return response, 200

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@limiter.limit("10 per minute")
def refresh():
    current_user_id = get_jwt_identity()
    user = get_user_by_id(int(current_user_id))
    role = user.get("role", "user") if user else "user"
    
    new_access_token = create_access_token(
        identity=current_user_id,
        additional_claims={"role": role}
    )
    
    audit_log("TOKEN_REFRESH", current_user_id, "Access token refreshed")
    
    return jsonify({
        "message": "Access token refreshed",
        "access_token": new_access_token
    }), 200

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    
    if hasattr(request, 'user_id'):
        audit_log("LOGOUT", request.user_id, "User logged out")
    
    return response, 200

# ==========================================
# BOOKS ENDPOINTS
# ==========================================

@app.route('/api/v2/books', methods=['GET'])
@limiter.limit("30 per minute")
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
# BORROWING OPERATIONS
# ==========================================

@app.route('/users/<int:user_id>/borrowings', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def borrow_book(user_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if str(user_id) != current_user_id and claims.get("role") != "admin":
        security_logger.warning(
            f"User {current_user_id} attempted to borrow book for user {user_id}"
        )
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
    
    update_metrics()
    audit_log("BORROW_BOOK", user_id, f"Borrowed book_id={book_id} ({book['title']})")
    
    return jsonify({"message": f"{user['name']} borrowed {book['title']}"})

@app.route('/users/<int:user_id>/returnings', methods=['POST'])
@jwt_required()
@limiter.limit("10 per hour")
def return_book(user_id):
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    
    if str(user_id) != current_user_id and claims.get("role") != "admin":
        security_logger.warning(
            f"User {current_user_id} attempted to return book for user {user_id}"
        )
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
        book_title = book['title']
    
    update_metrics()
    audit_log("RETURN_BOOK", user_id, f"Returned book_id={book_id} ({book_title})")

    return jsonify({"message": "Book returned successfully", "record": record})

# ==========================================
# MONITORING & HEALTH ENDPOINTS
# ==========================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancers"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/metrics', methods=['GET'])
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.route('/api/stats', methods=['GET'])
@jwt_required()
@admin_required()
def get_stats():
    """Get system statistics (admin only)"""
    total_books = len(books)
    available_books = len([b for b in books if b['available']])
    total_users = len(users)
    active_borrowings = len([b for b in borrowings if b['return_date'] is None])
    
    return jsonify({
        "books": {
            "total": total_books,
            "available": available_books,
            "borrowed": total_books - available_books
        },
        "users": {
            "total": total_users,
            "admins": len([u for u in users if u['role'] == 'admin']),
            "regular": len([u for u in users if u['role'] == 'user'])
        },
        "borrowings": {
            "active": active_borrowings,
            "total": len(borrowings)
        }
    })

# ==========================================
# HOME
# ==========================================

@app.route('/')
def home():
    return jsonify({
        "message": "Library Management API - Production Ready",
        "version": "1.0.0",
        "features": {
            "security": ["JWT Authentication", "Rate Limiting", "Role-based Access"],
            "monitoring": ["Prometheus Metrics", "Structured Logging", "Request Tracing"],
            "reliability": ["Circuit Breaker", "Health Checks", "Audit Logs"]
        },
        "endpoints": {
            "docs": "/apidocs",
            "health": "/health",
            "metrics": "/metrics (Prometheus format)",
            "stats": "/api/stats (admin only)"
        }
    })

# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    app_logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(error):
    app_logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    return jsonify({"error": "An unexpected error occurred"}), 500

# ==========================================
# STARTUP
# ==========================================

if __name__ == '__main__':
    # Create necessary directories
    for directory in ['openapi', 'logs']:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    # Initialize metrics
    update_metrics()
    
    # Log startup
    app_logger.info("=" * 60)
    app_logger.info("Library Management API Starting...")
    app_logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    app_logger.info("=" * 60)
    
    # Run application
    app.run(host='0.0.0.0', port=5000, debug=True)
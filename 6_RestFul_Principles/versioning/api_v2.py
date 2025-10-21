from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
import data


api_v2 = Blueprint('api_v2', __name__)


@api_v2.route('/books', methods=['GET'])
def get_books_v2():
    """Lấy danh sách sách (phiên bản 2: có phân trang)."""
    search = request.args.get('search', '').lower()
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 5))

    filtered = [b for b in data.books if search in b['title'].lower()]
    paginated = filtered[offset: offset + limit]

    return jsonify({
        "total": len(filtered),
        "offset": offset,
        "limit": limit,
        "data": paginated
    })

@api_v2.route('/books/<int:book_id>', methods=['GET'])
def get_book_v2(book_id):
    """Lấy chi tiết một cuốn sách (phiên bản 2: có thêm tên tác giả)."""
    book = next((b for b in data.books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
        
    author = next((a for a in data.authors if a['id'] == book.get('author_id')), None)
    
    book_with_author = book.copy()
    book_with_author['author_name'] = author['name'] if author else "Unknown"
    
    return jsonify(book_with_author)


@api_v2.route('/books', methods=['POST'])
@jwt_required()
def add_book():
    """Thêm một cuốn sách mới (yêu cầu xác thực JWT)."""
    req_data = request.get_json()
    if not req_data or 'title' not in req_data or 'author_id' not in req_data:
        return jsonify({"error": "Missing title or author_id"}), 400

    new_id = max([b["id"] for b in data.books]) + 1 if data.books else 1
    
    new_book = {
        "id": new_id,
        "title": req_data.get("title"),
        "author_id": req_data.get("author_id"),
        "available": True
    }
    data.books.append(new_book)
    return jsonify(new_book), 201

@api_v2.route('/books/<int:book_id>', methods=['PUT'])
@jwt_required()
def update_book(book_id):
    """Cập nhật thông tin một cuốn sách (yêu cầu xác thực JWT)."""
    book = next((b for b in data.books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    req_data = request.get_json()

    book['title'] = req_data.get('title', book['title'])
    book['author_id'] = req_data.get('author_id', book['author_id'])
    
    return jsonify(book)

@api_v2.route('/books/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book(book_id):
    """Xóa một cuốn sách (yêu cầu xác thực JWT)."""
    original_length = len(data.books)
    data.books = [b for b in data.books if b['id'] != book_id]
    
    if len(data.books) == original_length:
        return jsonify({"error": "Book not found"}), 404
        
    return jsonify({"message": f"Book with id {book_id} has been deleted."})


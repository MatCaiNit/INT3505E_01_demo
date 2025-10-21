# api_v1.py
from flask import Blueprint, jsonify, request
import data # Import dữ liệu từ data.py

# Định nghĩa một Blueprint tên là 'api_v1'
api_v1 = Blueprint('api_v1', __name__)

@api_v1.route('/books', methods=['GET'])
def get_books_v1():
    """Lấy danh sách sách (phiên bản 1: trả về list đơn giản)."""
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 5))
    
    paginated_books = data.books[offset : offset + limit]
    
    # V1 chỉ trả về một danh sách đơn giản
    return jsonify(paginated_books)

@api_v1.route('/books/<int:book_id>', methods=['GET'])
def get_book_v1(book_id):
    """Lấy chi tiết một cuốn sách (phiên bản 1)."""
    book = next((b for b in data.books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)

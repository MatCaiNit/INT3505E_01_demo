from flask import Flask, jsonify, request, make_response

library_api = Flask(__name__)

# "CSDL" tạm trong RAM
books = [
    {"id": 1, "title": "Đắc Nhân Tâm", "author": "Dale Carnegie", "available": True},
    {"id": 2, "title": "Sự im lặng của bầy cừu", "author": "Thomas Harris", "available": True},
    {"id": 3, "title": "Tuổi trẻ đáng giá bao nhiêu", "author": "Rosie Nguyễn", "available": False},
    {"id": 4, "title": "Nhà giả kim", "author": "Paulo Coelho", "available": True},
    {"id": 5, "title": "Đừng bao giờ từ bỏ ước mơ", "author": "Nick Vujicic", "available": True},
    {"id": 6, "title": "Bí mật tư duy triệu phú", "author": "T. Harv Eker", "available": False},
    {"id": 7, "title": "Đời ngắn đừng ngủ dài", "author": "Robin Sharma", "available": True},
    {"id": 8, "title": "Nhà giầu có nhất thành Babylon", "author": "George S. Clason", "available": True},
    {"id": 9, "title": "7 thói quen của người thành đạt", "author": "Stephen R. Covey", "available": True},
    {"id": 10, "title": "Đừng để con rùa chết khát", "author": "Nguyễn Nhật Ánh", "available": False},
    {"id": 11, "title": "Dạy con làm giàu", "author": "Robert T. Kiyosaki", "available": True},  
]
borrows = []


@library_api.route("/api/books", methods=["GET"])
def get_books():
    return jsonify(books)

@library_api.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Không tìm thấy sách trong thư viện"}), 404
    return jsonify(book)

@library_api.route("/api/books", methods=["POST"])
def add_book():
    data = request.get_json()
    new_book = {
        "id": len(books) + 1,
        "title": data["title"],
        "author": data["author"],
        "available": True
    }
    books.append(new_book)
    return jsonify(new_book), 201

@library_api.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Không tìm thấy sách trong thư viện"}), 404
    book.update({
        "title": data.get("title", book["title"]),
        "author": data.get("author", book["author"]),
        "available": data.get("available", book["available"])
    })
    return jsonify(book)

@library_api.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    global books
    books = [b for b in books if b["id"] != book_id]
    return jsonify({"message": f"Sách {book_id} đã xóa "})


@library_api.route("/api/books-cache", methods=["GET"])
@library_api.route("/api/books-cache/<int:book_id>", methods=["GET"])
def get_books_cache(book_id=None):
    if book_id:
        book = next((b for b in books if b["id"] == book_id), None)
        if not book:
            return jsonify({"error": "Không tìm thấy sách trong thư viện"}), 404
        data = book
    else:
        data = books

    response = make_response(jsonify(data))
    response.headers["Cache-Control"] = "public, max-age=60"
    return response


@library_api.route("/api/borrows", methods=["POST"])
def borrow_book():
    data = request.get_json()
    user_id = data.get("user_id")
    book_id = data.get("book_id")

    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Không tìm thấy sách trong thư viện"}), 400
    if not book["available"]:
        return jsonify({"error": "Sách hiện không có sẵn để mượn"}), 400

    book["available"] = False
    borrow = {"user_id": user_id, "book_id": book_id}
    borrows.append(borrow)
    return jsonify(borrow), 201

@library_api.route("/api/borrows/return", methods=["POST"])
def return_book():
    data = request.get_json()
    book_id = data.get("book_id")
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Không tìm thấy sách trong thư viện"}), 404
    book["available"] = True
    return jsonify({"message": "Sách đã trả lại thành công"})


@library_api.route("/api/code-on-demand", methods=["GET"])
def code_on_demand():
    return jsonify({
        "script": "print('Code on demand từ server!')"
    })


@library_api.route("/api/books-hateoas/<int:book_id>", methods=["GET"])
def get_book_hateoas(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Không tìm thấy sách trong thư viện"}), 404
    links = {
        "self": f"/api/books-hateoas/{book_id}",
        "all_books": "/api/books"
    }
    return jsonify({"book": book, "links": links})


@library_api.before_request
def middleware_layer():
    print("Lớp trung gian:", request.path)

@library_api.route("/api/books-layered/<int:book_id>", methods=["GET"])
def get_book_layered(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Không tìm thấy sách trong thư viện"}), 404
    return jsonify({"book": book, "layer": "qua lớp trung gian"})


if __name__ == "__main__":
    library_api.run(debug=True)

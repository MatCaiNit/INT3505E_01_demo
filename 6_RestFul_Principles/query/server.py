from flask import Flask, jsonify, request

app = Flask(__name__)


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

books = [
    {"id": 1, "title": "Clean Code", "author_id": 1},
    {"id": 2, "title": "The Pragmatic Programmer", "author_id": 2},
    {"id": 3, "title": "Refactoring", "author_id": 3},
    {"id": 4, "title": "Design Patterns", "author_id": 4},
    {"id": 5, "title": "Python Crash Course", "author_id": 5},
    {"id": 6, "title": "Đắc Nhân Tâm", "author_id": 6},
    {"id": 7, "title": "Sự im lặng của bầy cừu", "author_id": 7},
    {"id": 8, "title": "Tuổi trẻ đáng giá bao nhiêu", "author_id": 8},
    {"id": 9, "title": "Nhà giả kim", "author_id": 9},
    {"id": 10, "title": "Đừng bao giờ từ bỏ ước mơ", "author_id": 10},
    {"id": 11, "title": "Bí mật tư duy triệu phú", "author_id": 11},
    {"id": 12, "title": "Đời ngắn đừng ngủ dài", "author_id": 12},
    {"id": 13, "title": "Nhà giầu có nhất thành Babylon", "author_id": 13},
    {"id": 14, "title": "7 thói quen của người thành đạt", "author_id": 14},
    {"id": 15, "title": "Đừng để con rùa chết khát", "author_id": 15},
    {"id": 16, "title": "Dạy con làm giàu", "author_id": 16},
]


@app.route('/books_with_offset', methods=['GET'])
def books_with_offset():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 3))
    print(f"QUERY: SELECT * FROM books OFFSET {offset} LIMIT {limit}")
    paginated = books[offset: offset + limit]

    return jsonify({
        "offset": offset,
        "limit": limit,
        "data": paginated
    })


@app.route('/books_with_nplus1', methods=['GET'])
def books_with_nplus1():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 3))
    print(f"QUERY 1: SELECT * FROM books OFFSET {offset} LIMIT {limit}")
    paginated = books[offset: offset + limit]

    data = []
    for b in paginated:
        print(f"QUERY N: SELECT * FROM authors WHERE id={b['author_id']}")
        author = next((a for a in authors if a["id"] == b["author_id"]), None)
        data.append({
            "book_id": b["id"],
            "title": b["title"],
            "author": author["name"] if author else None
        })
    return jsonify(data)


@app.route('/books_with_join', methods=['GET'])
def books_with_join():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 3))
    print(f"QUERY: SELECT b.*, a.name FROM books b JOIN authors a ON b.author_id=a.id OFFSET {offset} LIMIT {limit}")

    paginated = books[offset: offset + limit]
    author_map = {a["id"]: a["name"] for a in authors}

    data = [{
        "book_id": b["id"],
        "title": b["title"],
        "author": author_map.get(b["author_id"])
    } for b in paginated]

    return jsonify(data)


@app.route('/books_with_inquery', methods=['GET'])
def books_with_inquery():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 3))
    print(f"QUERY 1: SELECT * FROM books OFFSET {offset} LIMIT {limit}")
    paginated = books[offset: offset + limit]

    author_ids = {b["author_id"] for b in paginated}
    print(f"QUERY 2: SELECT * FROM authors WHERE id IN {tuple(author_ids)}")

    author_map = {a["id"]: a["name"] for a in authors if a["id"] in author_ids}
    data = [{
        "book_id": b["id"],
        "title": b["title"],
        "author": author_map.get(b["author_id"])
    } for b in paginated]

    return jsonify(data)


@app.route('/books_with_cursor', methods=['GET'])
def books_with_cursor():
    last_id = int(request.args.get('cursor', 0))
    limit = int(request.args.get('limit', 3))
    print(f"QUERY: SELECT * FROM books WHERE id > {last_id} ORDER BY id LIMIT {limit}")

    paginated = [b for b in books if b["id"] > last_id][:limit]
    next_cursor = paginated[-1]["id"] if paginated else None

    return jsonify({
        "cursor": last_id,
        "next_cursor": next_cursor,
        "limit": limit,
        "data": paginated
    })


@app.route('/books_with_cursor_join', methods=['GET'])
def books_with_cursor_join():
    last_id = int(request.args.get('cursor', 0))
    limit = int(request.args.get('limit', 3))
    print(f"QUERY: SELECT b.*, a.name FROM books b JOIN authors a ON b.author_id=a.id WHERE b.id > {last_id} ORDER BY b.id LIMIT {limit}")

    paginated = [b for b in books if b["id"] > last_id][:limit]
    author_map = {a["id"]: a["name"] for a in authors}
    data = [{
        "book_id": b["id"],
        "title": b["title"],
        "author": author_map.get(b["author_id"])
    } for b in paginated]
    next_cursor = paginated[-1]["id"] if paginated else None

    return jsonify({
        "cursor": last_id,
        "next_cursor": next_cursor,
        "data": data
    })

def build_books_cache():
    author_lookup = {a["id"]: a["name"] for a in authors}
    cache = []
    for b in books:
        cache.append({
            "id": b["id"],
            "title": b["title"],
            "author_id": b["author_id"],
            "author_name": author_lookup.get(b["author_id"])
        })
    return cache

books_cache = build_books_cache()

@app.route('/books_with_cache', methods=['GET'])
def books_with_cache():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 5))
    paginated = books_cache[offset: offset + limit]

    print("QUERY 1: SELECT * FROM books_cache OFFSET", offset, "LIMIT", limit)

    return jsonify({
        "offset": offset,
        "limit": limit,
        "data": paginated
    })


@app.route('/books_with_window', methods=['GET'])
def books_with_window():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 3))
    start = (page - 1) * limit
    end = start + limit
    print(f"QUERY: SELECT * FROM (SELECT *, ROW_NUMBER() OVER (ORDER BY id) AS rn FROM books) WHERE rn BETWEEN {start+1} AND {end}")

    paginated = books[start:end]
    return jsonify({
        "page": page,
        "limit": limit,
        "data": paginated
    })


@app.route('/books_with_hybrid', methods=['GET'])
def books_with_hybrid():
    cursor = request.args.get('cursor')
    limit = int(request.args.get('limit', 3))

    if cursor:
        last_id = int(cursor)
        print(f"QUERY: SELECT * FROM books WHERE id > {last_id} ORDER BY id LIMIT {limit}")
        paginated = [b for b in books if b["id"] > last_id][:limit]
    else:
        offset = int(request.args.get('offset', 0))
        print(f"QUERY: SELECT * FROM books OFFSET {offset} LIMIT {limit}")
        paginated = books[offset: offset + limit]

    next_cursor = paginated[-1]["id"] if paginated else None
    return jsonify({
        "next_cursor": next_cursor,
        "data": paginated
    })


@app.route('/')
def index():
    return jsonify({
        "routes": {
            "/books_with_offset": "Phân trang cơ bản bằng OFFSET/LIMIT",
            "/books_with_nplus1": "Ví dụ gây lỗi N+1 query",
            "/books_with_join": "Giải pháp JOIN tránh N+1",
            "/books_with_inquery": "Giải pháp IN query (batch load)",
            "/books_with_cursor": "Phân trang bằng cursor",
            "/books_with_cursor_join": "Cursor + JOIN (hiệu năng cao)",
            "/books_with_cache": "Denormalization / cache sẵn dữ liệu",
            "/books_with_window": "Window function pagination (ROW_NUMBER)",
            "/books_with_hybrid": "Hybrid offset + cursor pagination"
        }
    })


if __name__ == '__main__':
    app.run(debug=True)

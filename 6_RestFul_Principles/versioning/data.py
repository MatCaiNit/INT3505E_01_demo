#data.py
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
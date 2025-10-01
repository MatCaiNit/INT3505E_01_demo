import requests, json

base_url = "http://127.0.0.1:5000"

print("===== MENU =====")
print("1. Xem tất cả sách")
print("2. Mượn sách")
print("3. Trả sách")
choice = input("Chọn chức năng: ").strip()

if choice == "1":
    r = requests.get(f"{base_url}/api/books")
    print(json.dumps(r.json(), indent=4, ensure_ascii=False))

elif choice == "2":
    user_id = input("Nhập ID người dùng: ").strip()
    book_id = input("Nhập ID sách muốn mượn: ").strip()
    payload = {"user_id": int(user_id), "book_id": int(book_id)}
    r = requests.post(f"{base_url}/api/borrows", json=payload)
    print("Kết quả mượn sách:")
    print(json.dumps(r.json(), indent=4, ensure_ascii=False))

elif choice == "3":
    book_id = input("Nhập ID sách muốn trả: ").strip()
    payload = {"book_id": int(book_id)}
    r = requests.post(f"{base_url}/api/borrows/return", json=payload)
    print("Kết quả trả sách:")
    print(json.dumps(r.json(), indent=4, ensure_ascii=False))

else:
    print("Lựa chọn không hợp lệ")

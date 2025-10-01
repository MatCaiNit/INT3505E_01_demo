from flask import json
import requests

base_url = "http://127.0.0.1:5000/api/books"

book_id = input("Nhập ID sách muốn xem (0 để xem tất cả): ").strip()

if book_id == "0":
    url = base_url              
else:
    url = f"{base_url}/{book_id}"

r = requests.get(url)

if r.status_code == 200:
    print("===== Book Data =====")
    print(json.dumps(r.json(), indent=4, ensure_ascii=False))
else:
    print("Lỗi:", r.json())

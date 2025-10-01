import json
import requests, time

base_url = "http://127.0.0.1:5000/api/books-cache"

book_id = input("Nhập ID sách muốn xem (0 để xem tất cả): ").strip()

if book_id == "0":
    url = base_url              
else:
    url = f"{base_url}/{book_id}"

print("Lần 1:")
r1 = requests.get(url)
print("===== Book Data =====")
print(json.dumps(r1.json(), indent=4, ensure_ascii=False))
print("Cache-Control:", r1.headers.get("Cache-Control"))

time.sleep(5)
print("\nLần 2 (sau 5s):")
r2 = requests.get(url)
print("===== Book Data =====")
print(json.dumps(r2.json(), indent=4, ensure_ascii=False))
print("Cache-Control:", r2.headers.get("Cache-Control"))

import requests, json

base_url = "http://127.0.0.1:5000/api/books-hateoas"

book_id = input("Nhập ID sách muốn xem (0 để xem tất cả): ").strip()

if book_id == "0":
    url = base_url              
else:
    url = f"{base_url}/{book_id}"

r = requests.get(url)
data = r.json()

print("===== Book Data =====")
print(json.dumps(data["book"], indent=4, ensure_ascii=False))

print("\n===== Links từ server =====")
print(json.dumps(data["links"], indent=4, ensure_ascii=False))


all_books_url = f"http://127.0.0.1:5000{data['links']['all_books']}"
r2 = requests.get(all_books_url)

print("\n===== Tất cả Books =====")
print(json.dumps(r2.json(), indent=4, ensure_ascii=False))

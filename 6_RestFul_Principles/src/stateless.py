import requests

BASE_URL = "http://localhost:5000"

def demo_stateless():
    print("=== DEMO: STATELESS ===")

    user_id = 1
    book_id = 2
    print(f"\n[POST] User {user_id} borrow book {book_id}")
    res = requests.post(f"{BASE_URL}/users/{user_id}/borrowings", json={"book_id": book_id})
    print(res.json())

    print(f"\n[POST] User {user_id} return book {book_id}")
    res = requests.post(f"{BASE_URL}/users/{user_id}/return", json={"book_id": book_id})
    print(res.json())


if __name__ == "__main__":
    demo_stateless()

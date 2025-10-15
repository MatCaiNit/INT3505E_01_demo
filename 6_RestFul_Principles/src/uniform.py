import requests
from pprint import pprint

BASE_URL = "http://localhost:5000"

def demo_resource_identification():
    print("\n=== Resource Identification in Requests ===")
    print("[GET] /books")
    res_all = requests.get(f"{BASE_URL}/books")
    pprint(res_all.json())

    print("\n[GET] /books/1")
    res_one = requests.get(f"{BASE_URL}/books/1")
    print(res_one.json())

def demo_resource_manipulation():
    print("\n=== Manipulation of Resources Through Representations ===")

    print("[POST] /books")
    new_book = {"title": "Domain-Driven Design", "author_id": 1}
    res_post = requests.post(f"{BASE_URL}/books", json=new_book)
    pprint(res_post.json())

    print("\n[PUT] /books/1 — cập nhật title")
    update_data = {"title": "Clean Code (Updated Edition)"}
    res_put = requests.put(f"{BASE_URL}/books/1", json=update_data)
    pprint(res_put.json())


def demo_self_descriptive_messages():
    print("\n=== Self-Descriptive Messages ===")

    res = requests.get(f"{BASE_URL}/books/1")
    print(f"Status: {res.status_code}")
    print("Headers:")
    for k, v in res.headers.items():
        print(f"  {k}: {v}")
    print("\nBody:")
    pprint(res.json())

def demo_hateoas():
    r = requests.get(BASE_URL)
    root = r.json()
    print("Root _links:", root["_links"])

    books_url = BASE_URL + root["_links"]["books"]
    r = requests.get(books_url)
    books = r.json()
    print("Books first item _links:", books["data"][0]["_links"])

    author_url = BASE_URL + books["data"][0]["_links"]["author"]
    r = requests.get(author_url)
    author = r.json()
    print("Author detail:", author)


if __name__ == "__main__":
    demo_resource_identification()
    demo_resource_manipulation()
    demo_self_descriptive_messages()
    demo_hateoas()

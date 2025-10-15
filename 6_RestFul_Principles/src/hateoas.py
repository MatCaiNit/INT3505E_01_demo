import requests

BASE_URL = "http://localhost:5000"

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
    demo_hateoas()

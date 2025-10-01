import requests

url = "http://127.0.0.1:5000/api/books"
r = requests.get(url)
print("Ví dụ về Uniform interface:", r.json())

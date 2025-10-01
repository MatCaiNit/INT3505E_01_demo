import requests

url = "http://127.0.0.1:5000/api/books-layered/1"
r = requests.get(url)
print("Lớp:", r.json())

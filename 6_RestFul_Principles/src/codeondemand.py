import requests

url = "http://127.0.0.1:5000/api/code-on-demand"
r = requests.get(url)
data = r.json()
print("===== Chạy lệnh từ server =====")
exec(data["script"])

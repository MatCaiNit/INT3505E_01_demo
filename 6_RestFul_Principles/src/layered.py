import requests

BASE_URL = "http://localhost:5000"

def demo_layered():
    print("=== DEMO: LAYERED SYSTEM ===")
    try:
        res = requests.get(f"{BASE_URL}/health")
        if res.status_code == 200:
            print("Server healthy:", res.json())
            books_res = requests.get(f"{BASE_URL}/books")
            print("Gọi tầng ứng dụng chính /books:")
            print(books_res.json())
        else:
            print("Proxy layer từ chối gọi tầng ứng dụng")
    except Exception as e:
        print("Server không phản hồi:", e)

if __name__ == "__main__":
    demo_layered()

import requests
import time
from pprint import pprint

BASE_URL = "http://localhost:5000"
cache = {}

def demo_self_descriptive():
    print("=== DEMO: CACHEABLE ===")
    url = f"{BASE_URL}/books/1"

    # Lần 1: gọi server
    if url in cache and (time.time() - cache[url]["time"]) < 30:
        print("Dữ liệu từ cache:")
        pprint(cache[url]["data"])
    else:
        res = requests.get(url)
        print("Status:", res.status_code)
        print("Headers:")
        for k, v in res.headers.items():
            if k.lower() in ["cache-control", "content-type"]:
                print(f"  {k}: {v}")
        data = res.json()
        cache[url] = {"data": data, "time": time.time()}
        print("Dữ liệu từ server:")
        pprint(data)

    print("\nGọi lại sau 5s...")
    time.sleep(5)
    if url in cache and (time.time() - cache[url]["time"]) < 30:
        print("Dữ liệu từ cache:")
        pprint(cache[url]["data"])

if __name__ == "__main__":
    demo_self_descriptive()

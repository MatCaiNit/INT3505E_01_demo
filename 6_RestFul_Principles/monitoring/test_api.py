import requests
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
import json

BASE_URL = "http://localhost:5000"

# Test users
TEST_USERS = [
    {"name": "Quynh", "role": "admin"},
    {"name": "Chiến", "role": "admin"},
    {"name": "Đức", "role": "user"},
    {"name": "Khánh", "role": "user"}
]

# Store tokens for authenticated requests
tokens = {}

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def login_user(username):
    """Login and store token"""
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"name": username},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            tokens[username] = data.get('access_token')
            print(f"✅ {username} logged in successfully")
            return True
        else:
            print(f"❌ {username} login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {username} login error: {e}")
        return False

def test_failed_auth():
    """Generate failed authentication attempts"""
    print_section("TEST 1: Failed Authentication Attempts")
    
    # Test with wrong usernames
    wrong_users = ["hacker123", "admin", "root", "test", "anonymous"]
    
    for user in wrong_users:
        try:
            response = requests.post(
                f"{BASE_URL}/login",
                json={"name": user},
                timeout=5
            )
            print(f"  Attempted login with '{user}': {response.status_code}")
            time.sleep(0.2)
        except Exception as e:
            print(f"  Error: {e}")
    
    # Test with missing username
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={},
            timeout=5
        )
        print(f"  Attempted login without username: {response.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print(f"\n✅ Generated ~{len(wrong_users) + 1} failed auth attempts")

def test_login_all_users():
    """Login all valid users"""
    print_section("TEST 2: Login Valid Users (Active Users Metric)")
    
    for user in TEST_USERS:
        login_user(user['name'])
        time.sleep(0.3)
    
    print(f"\n✅ {len(tokens)} active users logged in")

def test_api_requests_basic():
    """Generate basic API requests"""
    print_section("TEST 3: Basic API Requests")
    
    endpoints = [
        "/api/v2/books",
        "/api/v2/books?page=1&per_page=5",
        "/api/v2/books?search=clean",
        "/health",
        "/"
    ]
    
    for endpoint in endpoints:
        for _ in range(5):
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                print(f"  GET {endpoint}: {response.status_code}")
                time.sleep(0.1)
            except Exception as e:
                print(f"  Error on {endpoint}: {e}")
    
    print(f"\n✅ Generated {len(endpoints) * 5} basic requests")

def test_concurrent_requests():
    """Simulate concurrent users"""
    print_section("TEST 4: Concurrent Requests (Request Rate)")
    
    def make_request():
        endpoints = [
            "/api/v2/books",
            "/api/v2/books?page=2",
            "/health"
        ]
        endpoint = random.choice(endpoints)
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            return response.status_code
        except:
            return None
    
    print("  Simulating 50 concurrent requests...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: make_request(), range(50)))
    
    success = len([r for r in results if r == 200])
    print(f"\n✅ Completed 50 concurrent requests ({success} successful)")

def test_borrow_return_books():
    """Test borrowing and returning books"""
    print_section("TEST 5: Borrow & Return Books (Books Available Metric)")
    
    if not tokens:
        print("❌ No logged in users. Skipping...")
        return
    
    # Get a user token
    user = "Đức"
    token = tokens.get(user)
    
    if not token:
        print(f"❌ {user} not logged in. Skipping...")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get user ID (assuming Đức is user_id=3)
    user_id = 3
    
    # Borrow multiple books
    book_ids = [1, 3, 4, 5]  # Available books
    
    print(f"\n  📚 {user} borrowing books...")
    for book_id in book_ids:
        try:
            response = requests.post(
                f"{BASE_URL}/users/{user_id}/borrowings",
                headers=headers,
                json={"book_id": book_id},
                timeout=5
            )
            if response.status_code == 200:
                print(f"    ✅ Borrowed book {book_id}")
            else:
                print(f"    ⚠️  Book {book_id}: {response.json().get('error', 'Failed')}")
            time.sleep(0.5)
        except Exception as e:
            print(f"    ❌ Error borrowing book {book_id}: {e}")
    
    # Wait a bit
    print("\n  ⏳ Waiting 2 seconds...")
    time.sleep(2)
    
    # Return some books
    print(f"\n  📖 {user} returning books...")
    return_books = book_ids[:2]  # Return first 2 books
    
    for book_id in return_books:
        try:
            response = requests.post(
                f"{BASE_URL}/users/{user_id}/returnings",
                headers=headers,
                json={"book_id": book_id},
                timeout=5
            )
            if response.status_code == 200:
                print(f"    ✅ Returned book {book_id}")
            else:
                print(f"    ⚠️  Book {book_id}: {response.json().get('error', 'Failed')}")
            time.sleep(0.5)
        except Exception as e:
            print(f"    ❌ Error returning book {book_id}: {e}")
    
    print(f"\n✅ Borrowed {len(book_ids)} books, returned {len(return_books)} books")

def test_request_latency():
    """Generate requests with different latencies"""
    print_section("TEST 6: Request Latency (Different Response Times)")
    
    print("  Creating requests with varying complexity...")
    
    # Fast requests
    for i in range(10):
        requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"    Fast request {i+1}/10")
        time.sleep(0.1)
    
    # Medium requests
    for i in range(10):
        requests.get(f"{BASE_URL}/api/v2/books?page=1&per_page=10", timeout=5)
        print(f"    Medium request {i+1}/10")
        time.sleep(0.15)
    
    # Slow requests (if you have authenticated endpoints)
    if tokens:
        admin_token = tokens.get("Quynh")
        if admin_token:
            headers = {"Authorization": f"Bearer {admin_token}"}
            for i in range(5):
                try:
                    requests.get(f"{BASE_URL}/api/stats", headers=headers, timeout=5)
                    print(f"    Slow request {i+1}/5")
                    time.sleep(0.2)
                except:
                    pass
    
    print(f"\n✅ Generated requests with varying latencies")

def test_status_codes():
    """Generate different status codes"""
    print_section("TEST 7: Different Status Codes")
    
    # 200 OK
    print("  Generating 200 OK responses...")
    for _ in range(10):
        requests.get(f"{BASE_URL}/api/v2/books", timeout=5)
    
    # 404 Not Found
    print("  Generating 404 Not Found responses...")
    for _ in range(5):
        requests.get(f"{BASE_URL}/api/v2/books/99999", timeout=5)
        requests.get(f"{BASE_URL}/nonexistent/endpoint", timeout=5)
    
    # 400 Bad Request (if token available)
    if tokens:
        user_token = tokens.get("Đức")
        if user_token:
            headers = {"Authorization": f"Bearer {user_token}"}
            print("  Generating 400 Bad Request responses...")
            for _ in range(3):
                requests.post(
                    f"{BASE_URL}/users/3/borrowings",
                    headers=headers,
                    json={},  # Missing book_id
                    timeout=5
                )
    
    # 401 Unauthorized
    print("  Generating 401 Unauthorized responses...")
    for _ in range(5):
        requests.post(f"{BASE_URL}/users/1/borrowings", json={"book_id": 1}, timeout=5)
    
    print(f"\n✅ Generated mixed status codes (200, 400, 401, 404)")

def test_endpoints_distribution():
    """Generate requests to different endpoints"""
    print_section("TEST 8: Requests by Endpoint Distribution")
    
    endpoint_requests = {
        "/api/v2/books": 20,
        "/health": 15,
        "/": 10,
        "/metrics": 5,
    }
    
    for endpoint, count in endpoint_requests.items():
        print(f"  Calling {endpoint} {count} times...")
        for _ in range(count):
            try:
                requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                time.sleep(0.05)
            except:
                pass
    
    print(f"\n✅ Generated distributed requests across endpoints")

def test_rate_limiting():
    """Test rate limiting (will generate 429 errors)"""
    print_section("TEST 9: Rate Limiting Test")
    
    print("  Sending rapid requests to trigger rate limit...")
    
    success_count = 0
    rate_limited_count = 0
    
    for i in range(60):  # Send 60 requests quickly
        try:
            response = requests.get(f"{BASE_URL}/api/v2/books", timeout=5)
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"    ⚠️  Rate limited at request {i+1}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        time.sleep(0.05)
    
    print(f"\n✅ Success: {success_count}, Rate Limited: {rate_limited_count}")

def continuous_load():
    """Generate continuous background load"""
    print_section("TEST 10: Continuous Background Load (30 seconds)")
    
    def background_requests():
        endpoints = ["/api/v2/books", "/health", "/"]
        for _ in range(100):
            endpoint = random.choice(endpoints)
            try:
                requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            except:
                pass
            time.sleep(random.uniform(0.1, 0.5))
    
    print("  Starting background load (3 threads)...")
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=background_requests)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Let it run for 30 seconds
    time.sleep(30)
    
    print(f"\n✅ Background load completed")

def check_metrics():
    """Check current metrics"""
    print_section("FINAL: Check Prometheus Metrics")
    
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=5)
        if response.status_code == 200:
            metrics_text = response.text
            
            # Extract key metrics
            print("\n📊 Current Metrics:")
            
            if "api_requests_total" in metrics_text:
                print("  ✅ api_requests_total - Found")
            
            if "api_request_duration_seconds" in metrics_text:
                print("  ✅ api_request_duration_seconds - Found")
            
            if "active_users_total" in metrics_text:
                print("  ✅ active_users_total - Found")
            
            if "books_available_total" in metrics_text:
                print("  ✅ books_available_total - Found")
            
            if "failed_auth_attempts_total" in metrics_text:
                print("  ✅ failed_auth_attempts_total - Found")
            
            print(f"\n📝 Full metrics available at: {BASE_URL}/metrics")
        else:
            print(f"❌ Failed to fetch metrics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking metrics: {e}")

def main():
    """Run all tests"""
    print("\n" + "🚀 "*30)
    print("  LIBRARY API - COMPREHENSIVE METRICS TEST")
    print("🚀 "*30)
    
    print(f"\n📍 Testing API at: {BASE_URL}")
    print("⏱️  Estimated time: ~2 minutes\n")
    
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not responding. Make sure Flask app is running!")
            return
        print("✅ API is running and healthy\n")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure Flask app is running on port 5000")
        return
    
    # Run all tests
    test_failed_auth()
    time.sleep(1)
    
    test_login_all_users()
    time.sleep(1)
    
    test_api_requests_basic()
    time.sleep(1)
    
    test_concurrent_requests()
    time.sleep(1)
    
    test_borrow_return_books()
    time.sleep(1)
    
    test_request_latency()
    time.sleep(1)
    
    test_status_codes()
    time.sleep(1)
    
    test_endpoints_distribution()
    time.sleep(1)
    
    test_rate_limiting()
    time.sleep(2)
    
    continuous_load()
    time.sleep(2)
    
    check_metrics()
    
    print("\n" + "="*60)
    print("  ✅ ALL TESTS COMPLETED!")
    print("="*60)
    print("\n📊 Next Steps:")
    print("  1. Open Grafana: http://localhost:3000")
    print("  2. Go to your 'Library API Monitoring' dashboard")
    print("  3. Set time range to 'Last 5 minutes'")
    print("  4. Set refresh to '5s'")
    print("  5. You should see all panels populated with data!")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
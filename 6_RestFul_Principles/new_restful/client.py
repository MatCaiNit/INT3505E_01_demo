import requests
import json

BASE_URL = "http://server:5000"

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def main():
    while True:
        print("\n===== MENU RESTFUL CLIENT =====")
        print("1. Xem tất cả sách")
        print("2. Xem chi tiết sách")
        print("3. Thêm sách")
        print("4. Cập nhật sách")
        print("5. Xóa sách")
        print("6. Mượn sách")
        print("7. Trả sách")
        print("8. Code on Demand (chạy code từ server)")
        print("0. Thoát")

        choice = input("Chọn chức năng: ").strip()

        try:
            if choice == "1":
                r = requests.get(f"{BASE_URL}/books")
                print_json(r.json())

            elif choice == "2":
                book_id = input("Nhập ID sách: ")
                r = requests.get(f"{BASE_URL}/books/{book_id}")
                if r.status_code == 200:
                    print_json(r.json())
                else:
                    print("Không tìm thấy sách!")

            elif choice == "3":
                title = input("Nhập tên sách: ")
                author_id = input("Nhập ID tác giả: ")
                r = requests.post(f"{BASE_URL}/books", json={"title": title, "author_id": int(author_id)})
                print_json(r.json())

            elif choice == "4":
                book_id = input("Nhập ID sách cần cập nhật: ")
                title = input("Tên mới: ")
                r = requests.put(f"{BASE_URL}/books/{book_id}", json={"title": title})
                print_json(r.json())

            elif choice == "5":
                book_id = input("Nhập ID sách cần xóa: ")
                r = requests.delete(f"{BASE_URL}/books/{book_id}")
                print("Đã xóa sách." if r.status_code == 200 else "Không tìm thấy sách!")

            elif choice == "6":
                user_id = input("Nhập ID người dùng: ")
                book_id = input("Nhập ID sách muốn mượn: ")
                r = requests.post(f"{BASE_URL}/users/{user_id}/borrowings", json={"book_id": int(book_id)})
                print_json(r.json())

            elif choice == "7":
                user_id = input("Nhập ID người dùng: ")
                book_id = input("Nhập ID sách muốn trả: ")
                r = requests.delete(f"{BASE_URL}/users/{user_id}/borrowings/{book_id}")
                print_json(r.json())

            elif choice == "8":
                print("Yêu cầu server gửi code và chạy thử...")
                r = requests.get(f"{BASE_URL}/code")
                code = r.text
                print("Code nhận được:\n", code)
                print("Kết quả chạy code:")
                exec(code)

            elif choice == "0":
                print("Thoát client.")
                break

            else:
                print("Lựa chọn không hợp lệ!")

        except Exception as e:
            print("Lỗi khi gọi API:", e)

if __name__ == "__main__":
    main()

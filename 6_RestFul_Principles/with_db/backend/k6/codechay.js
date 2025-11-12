import http from "k6/http";
import { check, group, sleep } from "k6";

export let options = {
    vus: 1,
    iterations: 1,
};

let baseUrl = "http://localhost:5000";

export default function () {
    let timestamp = Date.now();
    let testUsername = `user_${timestamp}`;
    let testEmail = `user_${timestamp}@example.com`;
    let jwtToken = "";
    let productId = "";
    let testProductName = `Sách Test ${timestamp}`;

    group("register", function () {
        let res = http.post(`${baseUrl}/register`, JSON.stringify({
            username: testUsername,
            password: "123456",
            email: testEmail,
            fullName: "Test User"
        }), {
            headers: { "Content-Type": "application/json" },
        });

        check(res, {
            "status is 201": (r) => r.status === 201,
            "message is correct": (r) => r.json().message === "Đăng ký thành công",
            "token exists": (r) => r.json().token !== undefined && r.json().token !== "",
        });

        jwtToken = res.json().token;
    });

    group("login", function () {
        let res = http.post(`${baseUrl}/login`, JSON.stringify({
            username: testUsername,
            password: "123456"
        }), {
            headers: { "Content-Type": "application/json" },
        });

        check(res, {
            "status is 200": (r) => r.status === 200,
            "token exists": (r) => r.json().token !== undefined,
        });

        jwtToken = res.json().token;
    });

    group("products", function () {
        // Lấy danh sách sản phẩm
        let resList = http.get(`${baseUrl}/products`, {
            headers: { Authorization: `Bearer ${jwtToken}` }
        });
        check(resList, {
            "status is 200": (r) => r.status === 200,
            "response is array": (r) => Array.isArray(r.json()),
        });

        // Tạo sản phẩm
        let resCreate = http.post(`${baseUrl}/products`, JSON.stringify({
            name: testProductName,
            category: "Tâm lý kỹ năng",
            type: "book",
            price: 135000,
            stock: 10,
            description: "Sách test tự động",
            images: ["https://example.com/images/test.jpg"]
        }), {
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${jwtToken}` },
        });

        check(resCreate, {
            "status is 201": (r) => r.status === 201,
            "product name matches": (r) => r.json().name === testProductName,
        });

        productId = resCreate.json()._id;

        // Lấy chi tiết sản phẩm
        if (productId) {
            let resDetail = http.get(`${baseUrl}/products/${productId}`, {
                headers: { Authorization: `Bearer ${jwtToken}` }
            });
            check(resDetail, {
                "status is 200": (r) => r.status === 200,
            });
        }

        // Cập nhật sản phẩm
        if (productId) {
            let resUpdate = http.put(`${baseUrl}/products/${productId}`, JSON.stringify({
                price: 150000,
                stock: 5
            }), {
                headers: { "Content-Type": "application/json", Authorization: `Bearer ${jwtToken}` },
            });
            check(resUpdate, {
                "status is 200": (r) => r.status === 200,
                "price updated": (r) => r.json().price === 150000,
            });
        }

        // Xóa sản phẩm
        if (productId) {
            let resDelete = http.del(`${baseUrl}/products/${productId}`, null, {
                headers: { Authorization: `Bearer ${jwtToken}` },
            });
            check(resDelete, { "status is 204": (r) => r.status === 204 });
        }
    });

    group("categories", function () {
        let res = http.get(`${baseUrl}/categories`);
        check(res, { "status is 200": (r) => r.status === 200 });
    });

    sleep(1);
}

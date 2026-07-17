import os
from pathlib import Path

DB = Path("test_aurelia.db")
if DB.exists():
    DB.unlink()

os.environ["DATABASE_URL"] = "sqlite:///./test_aurelia.db"
os.environ["ADMIN_EMAIL"] = "admin@aureliaboutique.com"
os.environ["ADMIN_PASSWORD"] = "ChangeMe123!"

from fastapi.testclient import TestClient  # noqa: E402

from app.db.session import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


def login(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_complete_boutique_purchase_and_admin_flow():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as client:
        register = client.post(
            "/api/v1/auth/register",
            json={"name": "Boutique Customer", "email": "customer@example.com", "password": "Customer123!"},
        )
        assert register.status_code == 201, register.text
        customer_headers = login(client, "customer@example.com", "Customer123!")

        products = client.get("/api/v1/products?featured=true").json()["items"]
        assert products and products[0]["variants"]
        product = products[0]
        variant = next(item for item in product["variants"] if item["stock"] > 0)

        cart = client.post(
            "/api/v1/cart/items",
            headers=customer_headers,
            json={"product_id": product["id"], "variant_id": variant["id"], "quantity": 1},
        )
        assert cart.status_code == 201, cart.text
        assert cart.json()["items"][0]["variant"]["size"] == variant["size"]

        checkout = client.post(
            "/api/v1/orders/checkout",
            headers=customer_headers,
            json={
                "shipping_name": "Boutique Customer",
                "shipping_phone": "9876543210",
                "shipping_address": "Dehradun, Uttarakhand",
                "payment_method": "mock_card",
                "coupon_code": "WELCOME15",
                "gift_note": "Please use gift packaging.",
            },
        )
        assert checkout.status_code == 201, checkout.text
        assert checkout.json()["items"][0]["size"] == variant["size"]
        assert checkout.json()["payment_status"] == "paid"

        admin_headers = login(client, "admin@aureliaboutique.com", "ChangeMe123!")
        dashboard = client.get("/api/v1/admin/dashboard", headers=admin_headers)
        assert dashboard.status_code == 200
        assert dashboard.json()["variants"] > 0

        new_category = client.post(
            "/api/v1/admin/categories",
            headers=admin_headers,
            json={
                "name": "Designer Edit",
                "slug": "designer-edit",
                "description": "Limited designer capsule",
                "image_url": "https://example.com/category.jpg",
                "is_active": True,
            },
        )
        assert new_category.status_code == 201, new_category.text

        create_product = client.post(
            "/api/v1/admin/products",
            headers=admin_headers,
            json={
                "title": "Test Designer Dress",
                "slug": "test-designer-dress",
                "brand": "Aurelia Test",
                "sku": "AT-TEST-01",
                "description": "A test garment used by the automated workflow.",
                "fabric": "Cotton silk",
                "fit": "Regular",
                "care_instructions": "Dry clean",
                "occasion": "Festive",
                "price": 2499,
                "compare_at_price": 2999,
                "image_url": "https://example.com/dress.jpg",
                "gallery_urls": "",
                "vendor": "Aurelia Verified",
                "weight_grams": 500,
                "featured": False,
                "bestseller": False,
                "published": True,
                "category_id": new_category.json()["id"],
                "variants": [
                    {"sku": "AT-TEST-01-PK-M", "size": "M", "color": "Pink", "stock": 8, "additional_price": 0, "is_active": True},
                    {"sku": "AT-TEST-01-PK-L", "size": "L", "color": "Pink", "stock": 6, "additional_price": 100, "is_active": True},
                ],
            },
        )
        assert create_product.status_code == 201, create_product.text
        assert create_product.json()["stock"] == 14

        update_status = client.patch(
            f"/api/v1/admin/orders/{checkout.json()['id']}/status",
            headers=admin_headers,
            json={"status": "confirmed"},
        )
        assert update_status.status_code == 200
        assert update_status.json()["status"] == "confirmed"

    if DB.exists():
        DB.unlink()

import json
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Order, OrderItem, Product


class StorefrontTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            title="Test Book",
            author="A. Writer",
            description="A short test description.",
            price=Decimal("25.00"),
            image="AtomicHabits.jpg",
            stock=5,
        )

    def post_json(self, path, data):
        return self.client.post(
            path,
            data=json.dumps(data),
            content_type="application/json",
        )

    def test_book_pages_render_database_products(self):
        listing = self.client.get("/books.html")
        detail = self.client.get(f"/book/{self.product.pk}/")

        self.assertContains(listing, "Test Book")
        self.assertContains(listing, "/static/js/script%20(1).js")
        self.assertContains(detail, "A short test description.")
        self.assertContains(detail, "R25.00")

    def test_cart_is_session_backed_and_checks_stock(self):
        response = self.post_json(
            "/api/cart/add/",
            {"product_id": self.product.pk, "quantity": 2},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["quantity"], 2)
        self.assertEqual(response.json()["total"], "50.00")

        too_many = self.post_json(
            "/api/cart/add/",
            {"product_id": self.product.pk, "quantity": 4},
        )
        self.assertEqual(too_many.status_code, 400)
        self.assertEqual(self.client.get("/api/cart/").json()["items"][0]["quantity"], 2)

        updated = self.post_json(
            "/api/cart/update/",
            {"product_id": self.product.pk, "quantity": 3},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["total"], "75.00")
        removed = self.post_json(
            "/api/cart/remove/",
            {"product_id": self.product.pk},
        )
        self.assertEqual(removed.json()["items"], [])

    def test_registration_checkout_stock_and_order_history(self):
        self.post_json(
            "/api/cart/add/",
            {"product_id": self.product.pk, "quantity": 2},
        )
        unauthenticated = self.post_json("/api/orders/create/", {})
        self.assertEqual(unauthenticated.status_code, 401)

        registered = self.post_json(
            "/api/register/",
            {
                "full_name": "Taylor Reader",
                "email": "taylor@example.com",
                "password": "different-strong-pass-9384",
                "terms_accepted": True,
            },
        )
        self.assertEqual(registered.status_code, 201)
        self.assertTrue(User.objects.filter(email="taylor@example.com").exists())

        order_response = self.post_json(
            "/api/orders/create/",
            {
                "full_name": "Taylor Reader",
                "email": "taylor@example.com",
                "phone": "0600000000",
                "address": "1 Reading Road",
                "city": "Johannesburg",
                "postal_code": "2000",
            },
        )
        self.assertEqual(order_response.status_code, 201)
        self.assertEqual(order_response.json()["total"], "50.00")
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.get().quantity, 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.client.get("/api/cart/").json()["items"], [])
        self.assertEqual(len(self.client.get("/api/orders/").json()["orders"]), 1)

    def test_registration_requires_terms_and_login_checks_password(self):
        missing_terms = self.post_json(
            "/api/register/",
            {
                "full_name": "Taylor Reader",
                "email": "taylor@example.com",
                "password": "different-strong-pass-9384",
            },
        )
        self.assertEqual(missing_terms.status_code, 400)
        self.assertFalse(User.objects.exists())

        user = User.objects.create_user(
            username="reader@example.com",
            email="reader@example.com",
            password="different-strong-pass-9384",
        )
        wrong_password = self.post_json(
            "/api/login/",
            {"email": user.email, "password": "incorrect-password"},
        )
        self.assertEqual(wrong_password.status_code, 401)
        correct_password = self.post_json(
            "/api/login/",
            {"email": user.email, "password": "different-strong-pass-9384"},
        )
        self.assertEqual(correct_password.status_code, 200)

    def test_csrf_token_is_set_for_browser_requests(self):
        client = self.client_class(enforce_csrf_checks=True)
        response = client.get("/api/csrf/")

        self.assertEqual(response.status_code, 200)
        csrf_token = response.cookies["csrftoken"].value
        blocked = client.post(
            "/api/cart/add/",
            data=json.dumps({"product_id": self.product.pk, "quantity": 1}),
            content_type="application/json",
        )
        self.assertEqual(blocked.status_code, 403)
        accepted = client.post(
            "/api/cart/add/",
            data=json.dumps({"product_id": self.product.pk, "quantity": 1}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(accepted.status_code, 200)

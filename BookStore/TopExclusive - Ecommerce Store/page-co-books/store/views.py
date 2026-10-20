import json
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import Order, OrderItem, Product


def home(request):
    return render(request, "home.html")


def book_list(request):
    return render(
        request,
        "books.html",
        {"products": Product.objects.filter(is_active=True)},
    )


def book_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    return render(request, "book-details.html", {"product": product})


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def cart_page(request):
    return render(request, "cart.html")


def login_page(request):
    return render(request, "login.html")


def signup_page(request):
    return render(request, "signup.html")


def orders_page(request):
    return render(request, "orders.html")


@require_GET
@ensure_csrf_cookie
def csrf_token(request):
    return JsonResponse({"message": "CSRF cookie is ready."})


def json_body(request):
    try:
        payload = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def error_response(message, status=400):
    return JsonResponse({"error": message}, status=status)


def product_data(product):
    return {
        "id": product.pk,
        "title": product.title,
        "author": product.author,
        "description": product.description,
        "price": str(product.price),
        "image_url": static(f"images/{product.image}"),
        "stock": product.stock,
    }


@require_GET
def products_api(request):
    products = Product.objects.filter(is_active=True)
    return JsonResponse({"products": [product_data(book) for book in products]})


@require_GET
def product_api(request, product_id):
    product = Product.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        return error_response("Book not found.", status=404)
    return JsonResponse({"product": product_data(product)})


def current_cart(request):
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        return {}
    return cart


def cart_data(request):
    cart = current_cart(request)
    products = Product.objects.filter(
        pk__in=[int(product_id) for product_id in cart if str(product_id).isdigit()],
        is_active=True,
    )
    items = []
    total = Decimal("0.00")
    for product in products:
        quantity = cart.get(str(product.pk), cart.get(product.pk, 0))
        if not isinstance(quantity, int) or quantity < 1:
            continue
        subtotal = product.price * quantity
        total += subtotal
        items.append(
            {
                **product_data(product),
                "quantity": quantity,
                "subtotal": str(subtotal),
            }
        )
    return {"items": items, "total": str(total)}


@require_GET
def cart_api(request):
    return JsonResponse(cart_data(request))


@require_POST
def cart_add_api(request):
    payload = json_body(request)
    if payload is None:
        return error_response("The request must contain valid JSON.")
    try:
        product_id = int(payload.get("product_id"))
        quantity = int(payload.get("quantity", 1))
    except (TypeError, ValueError):
        return error_response("Choose a valid book and quantity.")
    if not 1 <= quantity <= 99:
        return error_response("Quantity must be between 1 and 99.")
    product = Product.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        return error_response("Book not found.", status=404)
    cart = current_cart(request)
    new_quantity = int(cart.get(str(product.pk), 0)) + quantity
    if new_quantity > product.stock:
        return error_response(f"Only {product.stock} copies are in stock.")
    cart[str(product.pk)] = new_quantity
    request.session["cart"] = cart
    return JsonResponse(cart_data(request))


@require_POST
def cart_update_api(request):
    payload = json_body(request)
    if payload is None:
        return error_response("The request must contain valid JSON.")
    try:
        product_id = int(payload.get("product_id"))
        quantity = int(payload.get("quantity"))
    except (TypeError, ValueError):
        return error_response("Choose a valid book and quantity.")
    if not 1 <= quantity <= 99:
        return error_response("Quantity must be between 1 and 99.")
    product = Product.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        return error_response("Book not found.", status=404)
    if quantity > product.stock:
        return error_response(f"Only {product.stock} copies are in stock.")
    cart = current_cart(request)
    if str(product.pk) not in cart:
        return error_response("That book is not in your cart.", status=404)
    cart[str(product.pk)] = quantity
    request.session["cart"] = cart
    return JsonResponse(cart_data(request))


@require_POST
def cart_remove_api(request):
    payload = json_body(request)
    if payload is None:
        return error_response("The request must contain valid JSON.")
    try:
        product_id = int(payload.get("product_id"))
    except (TypeError, ValueError):
        return error_response("Choose a valid book.")
    cart = current_cart(request)
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return JsonResponse(cart_data(request))


@require_POST
def register_api(request):
    payload = json_body(request)
    if payload is None:
        return error_response("The request must contain valid JSON.")
    full_name = str(payload.get("full_name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = payload.get("password", "")
    if payload.get("terms_accepted") is not True:
        return error_response("Please agree to the terms before creating an account.")
    if not full_name or len(full_name) > 100 or not email or len(email) > 254:
        return error_response("Enter your name and a valid email address.")
    if not isinstance(password, str):
        return error_response("Enter a valid password.")
    try:
        validate_email(email)
    except ValidationError:
        return error_response("Enter your name and a valid email address.")
    if User.objects.filter(username__iexact=email).exists():
        return error_response("An account with this email already exists.")
    user = User(username=email, email=email, first_name=full_name)
    try:
        validate_password(password, user)
    except ValidationError as exc:
        return error_response(" ".join(exc.messages))
    user.set_password(password)
    user.save()
    login(request, user)
    return JsonResponse({"message": "Your account was created.", "name": full_name}, status=201)


@require_POST
def login_api(request):
    payload = json_body(request)
    if payload is None:
        return error_response("The request must contain valid JSON.")
    email = str(payload.get("email", "")).strip().lower()
    password = payload.get("password", "")
    if not email or not isinstance(password, str) or not password:
        return error_response("Enter your email and password.")
    user = authenticate(request, username=email, password=password)
    if user is None:
        return error_response("The email or password is incorrect.", status=401)
    login(request, user)
    return JsonResponse({"message": "You are now logged in.", "name": user.first_name})


@require_POST
def logout_api(request):
    logout(request)
    return JsonResponse({"message": "You have been logged out."})


@require_GET
def current_user_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False})
    return JsonResponse(
        {
            "authenticated": True,
            "name": request.user.first_name or request.user.email,
        }
    )


@require_GET
def orders_api(request):
    if not request.user.is_authenticated:
        return error_response("Please log in to view your orders.", status=401)
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return JsonResponse(
        {
            "orders": [
                {
                    "id": order.pk,
                    "created_at": order.created_at.isoformat(),
                    "status": order.get_status_display(),
                    "total": str(order.total),
                    "items": [
                        {
                            "title": item.title,
                            "price": str(item.price),
                            "quantity": item.quantity,
                        }
                        for item in order.items.all()
                    ],
                }
                for order in orders
            ]
        }
    )


@require_POST
@transaction.atomic
def create_order(request):
    if not request.user.is_authenticated:
        return error_response("Please log in before placing an order.", status=401)
    payload = json_body(request)
    if payload is None:
        return error_response("The request must contain valid JSON.")
    required_fields = ("full_name", "email", "phone", "address", "city", "postal_code")
    details = {field: str(payload.get(field, "")).strip() for field in required_fields}
    limits = {
        "full_name": 100,
        "email": 254,
        "phone": 30,
        "address": 250,
        "city": 100,
        "postal_code": 20,
    }
    if any(not value for value in details.values()):
        return error_response("Complete all delivery fields before placing your order.")
    if any(len(details[field]) > limit for field, limit in limits.items()):
        return error_response("One or more delivery fields are too long.")
    try:
        validate_email(details["email"])
    except ValidationError:
        return error_response("Enter a valid email address.")

    cart = current_cart(request)
    product_ids = sorted(int(product_id) for product_id in cart if str(product_id).isdigit())
    products = list(
        Product.objects.select_for_update()
        .filter(pk__in=product_ids, is_active=True)
        .order_by("pk")
    )
    if not products:
        return error_response("Your cart is empty.")
    if len(products) != len(product_ids):
        return error_response("A book in your cart is no longer available.")

    line_items = []
    total = Decimal("0.00")
    for product in products:
        quantity = cart.get(str(product.pk), 0)
        if not isinstance(quantity, int) or quantity < 1 or quantity > product.stock:
            return error_response(f"Not enough stock for {product.title}.")
        line_items.append((product, quantity))
        total += product.price * quantity

    order = Order.objects.create(
        user=request.user,
        total=total,
        **details,
    )
    for product, quantity in line_items:
        OrderItem.objects.create(
            order=order,
            product=product,
            title=product.title,
            price=product.price,
            quantity=quantity,
        )
        product.stock -= quantity
        product.save(update_fields=["stock"])

    request.session["cart"] = {}
    return JsonResponse(
        {"message": "Your order has been placed.", "order_id": order.pk, "total": str(total)},
        status=201,
    )


@require_POST
def orders_create_api(request):
    return create_order(request)

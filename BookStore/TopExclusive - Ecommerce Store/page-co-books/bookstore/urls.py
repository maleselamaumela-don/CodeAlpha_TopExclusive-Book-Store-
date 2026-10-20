from django.contrib import admin
from django.urls import path

from store import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("home.html", views.home, name="home_page"),
    path("books.html", views.book_list, name="book_list"),
    path("book/<int:product_id>/", views.book_detail, name="book_detail"),
    path("about.html", views.about, name="about"),
    path("contact.html", views.contact, name="contact"),
    path("cart.html", views.cart_page, name="cart_page"),
    path("login.html", views.login_page, name="login_page"),
    path("signup.html", views.signup_page, name="signup_page"),
    path("orders.html", views.orders_page, name="orders_page"),
    path("api/csrf/", views.csrf_token, name="csrf_token"),
    path("api/products/", views.products_api, name="products_api"),
    path("api/products/<int:product_id>/", views.product_api, name="product_api"),
    path("api/cart/", views.cart_api, name="cart_api"),
    path("api/cart/add/", views.cart_add_api, name="cart_add_api"),
    path("api/cart/update/", views.cart_update_api, name="cart_update_api"),
    path("api/cart/remove/", views.cart_remove_api, name="cart_remove_api"),
    path("api/register/", views.register_api, name="register_api"),
    path("api/login/", views.login_api, name="login_api"),
    path("api/logout/", views.logout_api, name="logout_api"),
    path("api/me/", views.current_user_api, name="current_user_api"),
    path("api/orders/", views.orders_api, name="orders_api"),
    path("api/orders/create/", views.orders_create_api, name="orders_create_api"),
]

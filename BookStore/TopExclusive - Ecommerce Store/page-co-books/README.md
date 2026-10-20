# Page Co. Books: Django backend

This folder contains your existing `frontend` plus a Django backend. Django serves the current pages, stores books and orders in SQLite, keeps the cart in the server session, and handles account registration and login.

## Start the website on Windows

Open PowerShell in this folder (`page-co-books`) and run these commands:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_books
python manage.py runserver
```

Then open <http://127.0.0.1:8000/> in your browser. Keep the PowerShell window open while you use the website; press `Ctrl+C` there to stop Django.

If PowerShell blocks virtual-environment activation, you can run the virtual environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_books
.\.venv\Scripts\python.exe manage.py runserver
```

## What the backend does

- **Books:** The starter catalog is copied into the database by `seed_books`. Manage books and stock at `/admin/` after creating an administrator account with `python manage.py createsuperuser`.
- **Cart:** Book quantities are saved on the server in your browser's Django session, not in `localStorage`.
- **Accounts:** Sign up and log in using the existing pages. Your email address is used as your username.
- **Orders:** You must be logged in to place an order. Django checks stock, records the delivery details and item prices, reduces stock, and shows your previous orders on the My Orders page.

This starter checkout records an order; it does **not** take payment or arrange shipping.

## A few beginner terms

- A **model** in `store/models.py` describes the database tables (books, orders, and order items).
- A **view** in `store/views.py` handles a page or a request from the browser.
- **Migrations** (`makemigrations` and `migrate`) create or update the database tables from your models.
- The SQLite database is the `db.sqlite3` file in this folder. Keep it backed up if you need to keep the store's data.

The included Django settings are for local learning and development only (`DEBUG` is on and the secret key is a development placeholder). Do not deploy this configuration publicly; production needs a private secret key, `DEBUG=False`, and production host/security settings.

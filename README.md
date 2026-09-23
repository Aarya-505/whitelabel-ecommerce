# White-Label E-Commerce Platform

A customizable, full-featured Django e-commerce platform featuring a modern storefront, product catalog, session cart, wishlist, checkout flow, and custom administration dashboard.

## Features

- Modern, responsive storefront and product catalog
- Category browsing, filtering, search, and sorting
- Session-based shopping cart and wishlist
- Multi-image product galleries and related product recommendations
- Streamlined checkout and order management flow
- Custom administrative dashboard for inventory and orders
- Clean separation of configuration and secrets via environment variables

## Tech Stack

- Python 3.10+
- Django 5.x
- SQLite (Development) / PostgreSQL (Production)
- Pillow (Image Processing)

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### 1. Clone the Repository

```bash
git clone https://github.com/Aarya-505/whitelabel-ecommerce.git
cd whitelabel-ecommerce
```

### 2. Set Up a Virtual Environment

On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Update `.env` with your secret key, debug setting, and admin credentials.

### 5. Initialize the Database

Run migrations and load initial sample data:

```bash
python manage.py migrate
python seed_data.py
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Deployment on PythonAnywhere

1. Clone this repository into your PythonAnywhere account.
2. Create a virtual environment and install `requirements.txt`.
3. Configure the `.env` file with `DEBUG=False` and your PythonAnywhere domain in `ALLOWED_HOSTS`.
4. Run `python manage.py migrate`, `python seed_data.py`, and `python manage.py collectstatic`.
5. Configure the Web tab:
   - Source directory: `/home/<username>/whitelabel-ecommerce`
   - Virtualenv: `/home/<username>/.virtualenvs/<env-name>`
   - Static files: `/static/` -> `/home/<username>/whitelabel-ecommerce/staticfiles`
   - WSGI configuration file pointing to `config.settings`
6. Reload the web app.

## License

This project is licensed under the MIT License.

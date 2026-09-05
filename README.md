# SwiftLink - Production-Ready Flask URL Shortener

SwiftLink is a secure, maintainable, production-ready web application built with Python and Flask for shortening URLs, managing link ownership, enforcing password protection and expiration, tracking analytics, and providing a RESTful API.

---

## Features

- **User Authentication & Session Management**: Secure user registration, login, and logout using Flask-Login and Werkzeug password hashing.
- **User-Based Link Ownership**: Users own their shortened links, view personal analytics, and can delete only their own links.
- **Short URL Generation**: Cryptographically secure short code generation using Python `secrets` with automated database collision resolution.
- **Custom URL Aliases**: Real-time AJAX availability checking (`/check-alias`) with custom alias validation (regex, length limits, reserved route protection).
- **Password-Protected Short Links**: Passwords protecting individual short links are securely hashed with Werkzeug.
- **Link Expiration**: Configurable expiration periods (1 day, 7 days, 30 days, or Never) with dedicated expired page handling.
- **Strict Protocol Validation**: Only `http://` and `https://` schemes are permitted, blocking dangerous schemes (`javascript:`, `data:`).
- **Click Analytics**: Privacy-conscious click logging tracking timestamps, referrers, and device categories (Desktop, Mobile, Bot).
- **User Dashboard**: Metrics overview (Total Links, Total Clicks, Active, Protected, Expired), live search, pagination, copy link, and deletion.
- **RESTful API**: JSON API endpoints (`/api/v1/links`) for programmatically creating and querying shortened URLs with standard HTTP status codes.
- **Database Independence & Migrations**: Configurable database support (SQLite for local dev, PostgreSQL for production) managed with Flask-Migrate (Alembic).
- **Production & Container Readiness**: Gunicorn WSGI configuration, `Procfile`, `render.yaml`, `Dockerfile`, and `docker-compose.yml`.
- **Comprehensive Unit Testing**: Automated test suite powered by `pytest` covering authentication, URL operations, authorization, and API routes.

---

## Tech Stack

- **Backend**: Python 3.11+, Flask 3.1, Flask-SQLAlchemy, Flask-Login, Flask-Migrate (Alembic)
- **Database**: PostgreSQL (Production) / SQLite (Local Development)
- **Frontend**: HTML5, CSS3 (Custom responsive design), Vanilla JavaScript
- **Security**: Werkzeug Security (`generate_password_hash`, `check_password_hash`), HTTP-only & SameSite session cookies, scheme filtering
- **Production Server & DevOps**: Gunicorn, Docker, Docker Compose, Render Blueprint

---

## Directory Structure

```text
URL-Shortener/
├── app/
│   ├── __init__.py          # Application Factory (create_app)
│   ├── models.py            # User, Link, ClickLog SQLAlchemy models
│   ├── routes/
│   │   ├── auth.py          # Registration, Login, Logout routes
│   │   ├── links.py         # URL shortening, redirection, preview, password verification
│   │   ├── dashboard.py     # User-specific dashboard & analytics
│   │   └── api.py           # REST API endpoints (/api/v1/links)
│   ├── templates/
│   │   ├── base.html        # Shared base template with navbar & flash alerts
│   │   ├── index.html       # URL shortener interface
│   │   ├── dashboard.html   # User dashboard with stats & pagination
│   │   ├── password.html    # Password protection prompt page
│   │   ├── preview.html     # Link preview interstitial card
│   │   ├── login.html       # User login page
│   │   ├── register.html    # User registration page
│   │   ├── expired.html     # Expired link page
│   │   └── errors/          # Custom 404, 403, 500 error pages
│   └── static/
│       ├── script.js        # Enhanced JS (alias check, copy, search)
│       └── style.css        # Clean CSS design system
├── migrations/              # Flask-Migrate (Alembic) migration files
├── tests/
│   ├── conftest.py          # Pytest fixtures & test app setup
│   ├── test_auth.py         # Authentication unit tests
│   ├── test_links.py        # URL shortening, password, expiry tests
│   └── test_api.py          # REST API unit tests
├── config.py                # Configuration classes (Dev, Prod, Test)
├── app.py                   # Application entrypoint
├── wsgi.py                  # Gunicorn WSGI entrypoint
├── requirements.txt         # Dependencies list
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
├── Dockerfile               # Production Docker container setup
├── docker-compose.yml       # Local dev setup (Flask + PostgreSQL)
└── README.md                # Project documentation
```

---

## Installation & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/ChukkaDivya/URL-Shortner.git
cd URL-Shortner
```

### 2. Set up virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` if needed:
```ini
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
# DATABASE_URL=postgresql://user:password@localhost:5432/swiftlink_db
```

### 5. Run Database Migrations
```bash
flask db upgrade
```

### 6. Start Development Server
```bash
python app.py
```
Access the application at `http://127.0.0.1:5000`.

---

## Running with Docker Compose

To launch the application alongside a PostgreSQL database locally:
```bash
docker-compose up --build
```
Access the application at `http://localhost:5000`.

---

## Automated Testing

Run the full pytest test suite:
```bash
pytest -v
```
All 20 test cases cover authentication, short link creation, custom alias checks, password verification, expiration, authorization enforcement, click tracking, and REST API endpoints.

---

## REST API Documentation

### 1. Create Shortened URL
- **Endpoint**: `POST /api/v1/links`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "url": "https://example.com/long-page-path",
  "custom_alias": "mycustomalias",
  "expiry_days": 7,
  "password": "optionalpassword"
}
```
- **Response (201 Created)**:
```json
{
  "short_url": "http://127.0.0.1:5000/mycustomalias",
  "short_code": "mycustomalias",
  "original_url": "https://example.com/long-page-path",
  "created_at": "2026-09-05T11:18:31.064513+00:00",
  "expires_at": "2026-09-12T11:18:31.064513+00:00",
  "is_protected": true
}
```
- **Error Responses**:
  - `400 Bad Request`: Invalid URL format or scheme (`http://`/`https://` required).
  - `409 Conflict`: Custom alias already taken or reserved.

### 2. Retrieve Link Information
- **Endpoint**: `GET /api/v1/links/<short_code>`
- **Response (200 OK)**:
```json
{
  "short_code": "mycustomalias",
  "original_url": "https://example.com/long-page-path",
  "clicks": 14,
  "created_at": "2026-09-05T11:18:31.064513+00:00",
  "expires_at": "2026-09-12T11:18:31.064513+00:00",
  "is_protected": true,
  "is_expired": false
}
```
- **Error Responses**:
  - `404 Not Found`: Link does not exist.

---

## Deployment Instructions

### Deploying to Render
1. Create a Web Service on Render and connect your GitHub repository.
2. Render auto-detects `render.yaml` or set:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt && flask db upgrade`
   - **Start Command**: `gunicorn wsgi:app`
3. Attach a Render PostgreSQL Database and populate the `DATABASE_URL` environment variable.

---

## Security Considerations & Technical Limitations

### Security Features Implemented
- **Password Hashing**: User account passwords and short link passwords are stored as Werkzeug PBKDF2/scrypt hashes.
- **Strict Protocol Validation**: Prevents malicious URI schemes (e.g., `javascript:`, `data:`).
- **Authorization Enforcement**: Users can view and delete only their own links (`user_id` check returns `403 Forbidden`).
- **Session Security**: Session cookies set with `HttpOnly` and `SameSite=Lax`.
- **Environment Isolation**: Database URIs and Secret Keys are loaded exclusively from environment variables.

### Documented Technical Limitations
- **Guest Links**: Guest users can create shortened URLs without logging in, but guest links are unmanaged (cannot be edited or deleted unless logged in).
- **Preview Page**: SwiftLink renders an interstitial preview page before final redirect to protect users from malicious redirects.
- **Scale Limits**: Single-instance database transaction model; suitable for small-to-medium production traffic. For massive enterprise scale (millions of writes/sec), a distributed key-value store (e.g., Redis cluster) would be recommended.

---

## License

This project is open-source and available under the MIT License.

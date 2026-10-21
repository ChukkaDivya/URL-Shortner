# 🔗 SwiftLink — URL Shortener

SwiftLink is a secure URL-shortening web application built with Python and Flask. It allows users to create short links, manage URLs, protect links with passwords, set expiration dates, and track click analytics.

## 🌐 Live Demo

**[Try SwiftLink](https://swiftlink-app-w6n5.onrender.com)** | **[GitHub Repository](https://github.com/ChukkaDivya/URL-Shortner)**

## ✨ Key Features

- **User Authentication:** Secure registration, login, and logout.
- **URL Shortening:** Generate short, shareable links with collision-resistant codes.
- **Custom Aliases:** Create personalized short URLs with alias validation.
- **Password Protection:** Protect individual links using hashed passwords.
- **Link Expiration:** Set expiration periods or keep links active indefinitely.
- **Click Analytics:** Track clicks, referrers, and device categories.
- **User Dashboard:** Manage links, view statistics, search, paginate, and delete links.
- **URL Validation:** Accept only HTTP and HTTPS URL schemes.
- **REST API:** Create shortened links and retrieve link information through JSON endpoints.
- **Database Migrations:** Manage schema changes using Flask-Migrate and Alembic.

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, Flask 3.1
- **Database:** PostgreSQL (production), SQLite (local development)
- **ORM & Migrations:** Flask-SQLAlchemy, Flask-Migrate, Alembic
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Authentication:** Flask-Login, Werkzeug Security
- **Deployment:** Docker, Gunicorn, Render
- **Testing:** pytest
- **Version Control:** Git, GitHub

## 🚀 Run Locally

**1. Clone the repository**

```bash
git clone https://github.com/ChukkaDivya/URL-Shortner.git
cd URL-Shortner
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file using `.env.example` as a reference. Configure `SECRET_KEY` and the appropriate local database settings. Never commit secrets or production database credentials.

**5. Apply database migrations**

```bash
flask --app wsgi:app db upgrade
```

**6. Start the application**

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## 🔌 REST API

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/links` | Create a shortened URL |
| GET | `/api/v1/links/<short_code>` | Retrieve shortened-link information |

The API accepts JSON requests and returns JSON responses with appropriate HTTP status codes.

## ☁️ Deployment

SwiftLink is deployed on **Render** using Docker and PostgreSQL.

- **Live Application:** https://swiftlink-app-w6n5.onrender.com
- **Source Code:** https://github.com/ChukkaDivya/URL-Shortner

## 🧪 Testing

Run the automated test suite with:

```bash
pytest -v
```

## 👩‍💻 Author

**Divya**

GitHub: [@ChukkaDivya](https://github.com/ChukkaDivya)

---

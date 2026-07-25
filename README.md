# URL Shortener

A Flask-based URL Shortener web application that converts long URLs into secure, shareable short links. The application supports custom aliases, password protection, configurable link expiry, click analytics, and a dashboard for efficient link management.

## Features

- Generate unique short URLs
- Custom URL aliases
- Password-protected links
- Configurable link expiry
- URL validation
- Click analytics
- Dashboard for link management
- SQLite database integration

## Tech Stack

- Python
- Flask
- SQLAlchemy
- SQLite
- HTML
- CSS
- JavaScript

## Project Structure

```
URL-Shortener/
│── app.py
│── requirements.txt
│── instance/
│   └── database.db
│── static/
│   ├── style.css
│   └── script.js
│── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── preview.html
│   └── password.html
```

## How It Works

1. Enter a valid long URL.
2. Optionally add a custom alias, password, and expiry period.
3. The application generates a unique short URL.
4. The shortened URL is stored in the SQLite database.
5. Users are redirected to the original URL when accessing the short link.
6. Click analytics and link details are available in the dashboard.


## License

This project is intended for educational and learning purposes.

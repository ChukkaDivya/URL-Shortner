import os
from app import create_app, db

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # In development mode, run with debug enabled if FLASK_ENV is not production
    debug_mode = app.config.get('DEBUG', False)
    app.run(debug=debug_mode)
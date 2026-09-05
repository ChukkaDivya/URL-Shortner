import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config_by_name
from app.models import db, User

login_manager = LoginManager()
migrate = Migrate()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    config_cls = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_cls)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.links import links_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(links_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app

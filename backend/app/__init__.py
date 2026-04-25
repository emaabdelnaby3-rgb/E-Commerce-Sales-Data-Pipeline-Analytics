from flask import Flask, jsonify
from sqlalchemy import text

from app.api.admin import bp as admin_bp
from app.api.analytics import bp as analytics_bp
from app.api.auth import bp as auth_bp
from app.api.beneficiary import bp as beneficiary_bp
from app.api.donor import bp as donor_bp
from app.api.government import bp as government_bp
from app.config import Config
from app.core.errors import register_error_handlers
from app.extensions import bcrypt, db, jwt, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(beneficiary_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(government_bp)
    app.register_blueprint(analytics_bp)

    register_error_handlers(app)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/health/ready")
    def readiness():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ready", "database": "up"})
        except Exception:
            return jsonify({"status": "not_ready", "database": "down"}), 503

    return app

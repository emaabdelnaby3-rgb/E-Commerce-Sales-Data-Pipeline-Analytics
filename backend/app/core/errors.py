from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "bad_request", "message": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "unauthorized", "message": str(error)}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"error": "forbidden", "message": str(error)}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "not_found", "message": str(error)}), 404

    @app.errorhandler(SQLAlchemyError)
    def db_error(error):
        return jsonify({"error": "database_error", "message": "A database error occurred."}), 500

    @app.errorhandler(Exception)
    def unhandled(error):
        return jsonify({"error": "internal_server_error", "message": "An unexpected error occurred."}), 500

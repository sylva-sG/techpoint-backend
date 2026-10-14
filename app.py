from flask import Flask, jsonify, request 
from config import Config
from extensions import db, migrate, cors, jwt
from sqlalchemy import text
from models import User, Category, Product, Sale, SaleItem, StockMovement
from routes import (
    categories_bp,
    products_bp,
    restocks_bp,
    stock_bp,
    reports_bp,
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}})
    jwt.init_app(app)

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify(status="error", message="Authentication required"), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify(status="error", message="Invalid token"), 401

    @jwt.expired_token_loader
    def expired_token(header, payload):
        return jsonify(status="error",
                       message="Token expired, please log in again"), 401


    #test connection to postgresql
    @app.get("/api/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))

            return jsonify({
                "status": "success",
                "message": "POS API is running",
                "database": "connected"
            }), 200

        except Exception as e:
            db.session.rollback()

            return jsonify({
                "status": "error",
                "message": "Database connection failed",
                "error": str(e)
            }), 500
    
    app.register_blueprint(stock_bp)
    app.register_blueprint(restocks_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(reports_bp)
    return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], port=Config.PORT)

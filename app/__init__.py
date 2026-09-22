import os

from flask import Flask
from flask_login import current_user

from app.config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.auth.routes import auth_bp
    from app.shop.routes import shop_bp
    from app.seller.routes import seller_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(seller_bp)

    @app.context_processor
    def inject_globals():
        cart_count = 0
        if current_user.is_authenticated and current_user.is_customer:
            from app.models import CartItem

            cart_count = (
                db.session.query(db.func.coalesce(db.func.sum(CartItem.quantity), 0))
                .filter(CartItem.user_id == current_user.id)
                .scalar()
            )
        return {"cart_count": cart_count, "categories": app.config["CATEGORIES"]}

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    with app.app_context():
        db.create_all()
        if app.config.get("AUTO_SEED_DEMO_DATA"):
            from app.seed import ensure_seed_data

            ensure_seed_data()

    return app

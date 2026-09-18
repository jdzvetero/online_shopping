from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")  # customer | seller
    brand_name = db.Column(db.String(120))  # only used for sellers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship("Product", backref="seller", lazy=True)
    cart_items = db.relationship("CartItem", backref="user", lazy=True, cascade="all, delete-orphan")
    orders = db.relationship("Order", backref="customer", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_seller(self):
        return self.role == "seller"

    @property
    def is_customer(self):
        return self.role == "customer"


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, default="")
    category = db.Column(db.String(60), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(400), nullable=False)
    hover_image_url = db.Column(db.String(400))
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    variants = db.relationship("ProductVariant", backref="product", lazy=True, cascade="all, delete-orphan")

    @property
    def sizes(self):
        seen = []
        for v in self.variants:
            if v.size not in seen:
                seen.append(v.size)
        return seen

    @property
    def colors(self):
        seen = {}
        for v in self.variants:
            if v.color_name not in seen:
                seen[v.color_name] = v.color_hex
        return seen

    @property
    def total_stock(self):
        return sum(v.stock_quantity for v in self.variants if v.availability_status == "in_stock")

    @property
    def has_any_availability(self):
        return len(self.variants) > 0

    @property
    def lowest_available_status(self):
        """Returns overall badge status for the product card."""
        statuses = {v.availability_status for v in self.variants}
        if "in_stock" in statuses and any(
            v.availability_status == "in_stock" and v.stock_quantity > 0 for v in self.variants
        ):
            return "in_stock"
        if "preorder" in statuses:
            return "preorder"
        if "made_to_order" in statuses:
            return "made_to_order"
        return "unavailable"


class ProductVariant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    color_name = db.Column(db.String(60), nullable=False)
    color_hex = db.Column(db.String(10), nullable=False, default="#4169E1")
    sku = db.Column(db.String(60))
    stock_quantity = db.Column(db.Integer, default=0)
    # in_stock | preorder | made_to_order
    availability_status = db.Column(db.String(20), nullable=False, default="in_stock")
    available_date = db.Column(db.Date, nullable=True)  # for preorder
    lead_time_days = db.Column(db.Integer, nullable=True)  # for made_to_order

    cart_items = db.relationship("CartItem", backref="variant", lazy=True, cascade="all, delete-orphan")

    @property
    def is_purchasable(self):
        if self.availability_status == "in_stock":
            return self.stock_quantity > 0
        return True

    @property
    def availability_label(self):
        if self.availability_status == "in_stock":
            if self.stock_quantity <= 0:
                return "Out of stock"
            if self.stock_quantity <= 5:
                return f"Only {self.stock_quantity} left in stock"
            return "In stock"
        if self.availability_status == "preorder":
            if self.available_date:
                return f"Pre-order · Ships {self.available_date.strftime('%d %B %Y')}"
            return "Pre-order"
        if self.availability_status == "made_to_order":
            days = self.lead_time_days or 7
            if days % 7 == 0:
                weeks = days // 7
                span = f"{weeks} week" + ("s" if weeks != 1 else "")
            else:
                span = f"{days} days"
            return f"Made to order · Ready in {span}"
        return "Unavailable"

    @property
    def availability_eta(self):
        """Best-effort concrete date this variant will be ready."""
        if self.availability_status == "preorder" and self.available_date:
            return self.available_date
        if self.availability_status == "made_to_order":
            from datetime import timedelta
            days = self.lead_time_days or 7
            return date.today() + timedelta(days=days)
        return None


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("product_variant.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("user_id", "variant_id", name="uq_user_variant"),)

    @property
    def line_total(self):
        return round(self.quantity * self.variant.product.base_price, 2)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    fulfillment_type = db.Column(db.String(20), nullable=False)  # delivery | pickup
    status = db.Column(db.String(30), nullable=False, default="pending")

    subtotal = db.Column(db.Float, nullable=False)
    delivery_fee = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)

    # delivery details
    full_name = db.Column(db.String(160))
    phone = db.Column(db.String(40))
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    postal_code = db.Column(db.String(30))
    delivery_notes = db.Column(db.Text)

    # pickup details
    pickup_date = db.Column(db.Date)
    pickup_time = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    @property
    def status_label(self):
        return self.status.replace("_", " ").title()


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey("product_variant.id"), nullable=True)
    product_name = db.Column(db.String(160), nullable=False)
    image_url = db.Column(db.String(400))
    size = db.Column(db.String(10))
    color_name = db.Column(db.String(60))
    availability_label = db.Column(db.String(120))
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    @property
    def line_total(self):
        return round(self.unit_price * self.quantity, 2)

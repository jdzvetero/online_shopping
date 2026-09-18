from datetime import datetime, date, timedelta
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Product, ProductVariant, CartItem, Order, OrderItem

shop_bp = Blueprint("shop", __name__, template_folder="../templates/shop")


def customer_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_customer:
            flash("This area is for shoppers. You're logged in as a seller.", "info")
            return redirect(url_for("seller.dashboard"))
        return view(*args, **kwargs)

    return wrapped


@shop_bp.route("/")
def index():
    category = request.args.get("category")
    search = request.args.get("q", "").strip()
    sort = request.args.get("sort", "newest")

    query = Product.query.filter_by(is_active=True)
    if category and category in current_app.config["CATEGORIES"]:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if sort == "price_low":
        query = query.order_by(Product.base_price.asc())
    elif sort == "price_high":
        query = query.order_by(Product.base_price.desc())
    else:
        query = query.order_by(Product.created_at.desc())

    products = query.all()
    featured = Product.query.filter_by(is_active=True, is_featured=True).limit(4).all()

    return render_template(
        "shop/index.html",
        products=products,
        featured=featured,
        active_category=category,
        search=search,
        sort=sort,
    )


@shop_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    size_order = current_app.config["SIZE_ORDER"]
    sizes = sorted(product.sizes, key=lambda s: size_order.index(s) if s in size_order else 99)
    related = (
        Product.query.filter(Product.category == product.category, Product.id != product.id, Product.is_active == True)
        .limit(4)
        .all()
    )
    variants_data = [
        {
            "id": v.id,
            "size": v.size,
            "color_name": v.color_name,
            "status": v.availability_status,
            "label": v.availability_label,
            "purchasable": v.is_purchasable,
            "stock": v.stock_quantity,
        }
        for v in product.variants
    ]
    return render_template(
        "shop/product_detail.html",
        product=product,
        sizes=sizes,
        colors=product.colors,
        size_chart=current_app.config["SIZE_CHART"],
        related=related,
        variants_data=variants_data,
    )


@shop_bp.route("/cart/add", methods=["POST"])
@customer_required
def cart_add():
    variant_id = request.form.get("variant_id", type=int)
    quantity = max(1, request.form.get("quantity", 1, type=int))
    product_id = request.form.get("product_id", type=int)

    variant = ProductVariant.query.get(variant_id) if variant_id else None
    if variant is None:
        flash("Please select a size and colour before adding to bag.", "error")
        return redirect(url_for("shop.product_detail", product_id=product_id) if product_id else url_for("shop.index"))

    if variant.availability_status == "in_stock" and variant.stock_quantity < 1:
        flash("Sorry, that size/colour just sold out.", "error")
        return redirect(url_for("shop.product_detail", product_id=variant.product_id))

    existing = CartItem.query.filter_by(user_id=current_user.id, variant_id=variant.id).first()
    if existing:
        existing.quantity += quantity
    else:
        db.session.add(CartItem(user_id=current_user.id, variant_id=variant.id, quantity=quantity))
    db.session.commit()

    flash(f"Added “{variant.product.name}” to your bag.", "success")
    return redirect(url_for("shop.product_detail", product_id=variant.product_id))


@shop_bp.route("/cart/update/<int:item_id>", methods=["POST"])
@customer_required
def cart_update(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash("Not authorized.", "error")
        return redirect(url_for("shop.cart"))

    quantity = request.form.get("quantity", 1, type=int)
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    return redirect(url_for("shop.cart"))


@shop_bp.route("/cart/remove/<int:item_id>", methods=["POST"])
@customer_required
def cart_remove(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed from bag.", "info")
    return redirect(url_for("shop.cart"))


@shop_bp.route("/cart")
@customer_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    subtotal = round(sum(item.line_total for item in items), 2)
    return render_template("shop/cart.html", items=items, subtotal=subtotal)


@shop_bp.route("/checkout", methods=["GET", "POST"])
@customer_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash("Your bag is empty.", "info")
        return redirect(url_for("shop.index"))

    subtotal = round(sum(item.line_total for item in items), 2)
    delivery_fee = current_app.config["DELIVERY_FEE"]

    if request.method == "POST":
        fulfillment_type = request.form.get("fulfillment_type", "delivery")

        order = Order(
            user_id=current_user.id,
            fulfillment_type=fulfillment_type,
            status="confirmed",
            subtotal=subtotal,
        )

        if fulfillment_type == "delivery":
            required = ["full_name", "phone", "address_line1", "city", "region", "postal_code"]
            missing = [f for f in required if not request.form.get(f, "").strip()]
            if missing:
                flash("Please complete all required delivery details.", "error")
                return render_template(
                    "shop/checkout.html", items=items, subtotal=subtotal, delivery_fee=delivery_fee, form=request.form
                )
            order.full_name = request.form.get("full_name").strip()
            order.phone = request.form.get("phone").strip()
            order.address_line1 = request.form.get("address_line1").strip()
            order.address_line2 = request.form.get("address_line2", "").strip()
            order.city = request.form.get("city").strip()
            order.region = request.form.get("region").strip()
            order.postal_code = request.form.get("postal_code").strip()
            order.delivery_notes = request.form.get("delivery_notes", "").strip()
            order.delivery_fee = delivery_fee
            order.total = round(subtotal + delivery_fee, 2)
        else:
            pickup_date_str = request.form.get("pickup_date", "")
            pickup_time = request.form.get("pickup_time", "").strip()
            if not pickup_date_str or not pickup_time:
                flash("Please choose a pickup date and time.", "error")
                return render_template(
                    "shop/checkout.html", items=items, subtotal=subtotal, delivery_fee=delivery_fee, form=request.form
                )
            try:
                pickup_date = datetime.strptime(pickup_date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid pickup date.", "error")
                return render_template(
                    "shop/checkout.html", items=items, subtotal=subtotal, delivery_fee=delivery_fee, form=request.form
                )
            if pickup_date < date.today():
                flash("Pickup date must be in the future.", "error")
                return render_template(
                    "shop/checkout.html", items=items, subtotal=subtotal, delivery_fee=delivery_fee, form=request.form
                )
            order.full_name = request.form.get("full_name", current_user.name).strip() or current_user.name
            order.phone = request.form.get("phone", "").strip()
            order.pickup_date = pickup_date
            order.pickup_time = pickup_time
            order.delivery_fee = 0
            order.total = subtotal

        db.session.add(order)
        db.session.flush()

        for item in items:
            variant = item.variant
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    variant_id=variant.id,
                    product_name=variant.product.name,
                    image_url=variant.product.image_url,
                    size=variant.size,
                    color_name=variant.color_name,
                    availability_label=variant.availability_label,
                    unit_price=variant.product.base_price,
                    quantity=item.quantity,
                )
            )
            if variant.availability_status == "in_stock":
                variant.stock_quantity = max(0, variant.stock_quantity - item.quantity)
            db.session.delete(item)

        db.session.commit()
        return redirect(url_for("shop.order_confirmation", order_id=order.id))

    return render_template("shop/checkout.html", items=items, subtotal=subtotal, delivery_fee=delivery_fee, form={})


@shop_bp.route("/order/<int:order_id>/confirmation")
@customer_required
def order_confirmation(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash("Not authorized.", "error")
        return redirect(url_for("shop.index"))
    return render_template("shop/order_confirmation.html", order=order)


@shop_bp.route("/account/orders")
@customer_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("customer/orders.html", orders=orders)


@shop_bp.route("/api/variant/<int:variant_id>")
def api_variant(variant_id):
    variant = ProductVariant.query.get_or_404(variant_id)
    return jsonify(
        {
            "id": variant.id,
            "size": variant.size,
            "color_name": variant.color_name,
            "color_hex": variant.color_hex,
            "status": variant.availability_status,
            "label": variant.availability_label,
            "purchasable": variant.is_purchasable,
            "stock": variant.stock_quantity,
        }
    )

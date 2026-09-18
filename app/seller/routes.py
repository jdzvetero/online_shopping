from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Product, ProductVariant, Order, OrderItem

seller_bp = Blueprint("seller", __name__, url_prefix="/seller", template_folder="../templates/seller")


def seller_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_seller:
            flash("This area is for sellers. You're logged in as a shopper.", "info")
            return redirect(url_for("shop.index"))
        return view(*args, **kwargs)

    return wrapped


@seller_bp.route("/dashboard")
@seller_required
def dashboard():
    products = Product.query.filter_by(seller_id=current_user.id).order_by(Product.created_at.desc()).all()

    variant_ids = [v.id for p in products for v in p.variants]
    order_items = (
        OrderItem.query.filter(OrderItem.variant_id.in_(variant_ids)).all() if variant_ids else []
    )

    revenue = round(sum(oi.line_total for oi in order_items), 2)
    low_stock = [
        v for p in products for v in p.variants if v.availability_status == "in_stock" and 0 < v.stock_quantity <= 5
    ]
    out_of_stock = [
        v for p in products for v in p.variants if v.availability_status == "in_stock" and v.stock_quantity == 0
    ]

    distinct_order_ids = {oi.order_id for oi in order_items}

    return render_template(
        "seller/dashboard.html",
        products=products,
        revenue=revenue,
        order_count=len(distinct_order_ids),
        low_stock=low_stock,
        out_of_stock=out_of_stock,
    )


def _parse_variants_from_form(form):
    sizes = form.getlist("variant_size[]")
    color_names = form.getlist("variant_color_name[]")
    color_hexes = form.getlist("variant_color_hex[]")
    stocks = form.getlist("variant_stock[]")
    statuses = form.getlist("variant_status[]")
    dates = form.getlist("variant_date[]")
    leadtimes = form.getlist("variant_leadtime[]")

    variants = []
    for i in range(len(sizes)):
        size = sizes[i].strip().upper()
        color_name = color_names[i].strip() if i < len(color_names) else ""
        if not size or not color_name:
            continue
        status = statuses[i] if i < len(statuses) else "in_stock"
        variant = {
            "size": size,
            "color_name": color_name,
            "color_hex": color_hexes[i] if i < len(color_hexes) else "#4169E1",
            "availability_status": status,
            "stock_quantity": 0,
            "available_date": None,
            "lead_time_days": None,
        }
        if status == "in_stock":
            try:
                variant["stock_quantity"] = max(0, int(stocks[i]))
            except (ValueError, IndexError):
                variant["stock_quantity"] = 0
        elif status == "preorder":
            date_str = dates[i] if i < len(dates) else ""
            if date_str:
                try:
                    variant["available_date"] = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    pass
        elif status == "made_to_order":
            try:
                variant["lead_time_days"] = max(1, int(leadtimes[i]))
            except (ValueError, IndexError):
                variant["lead_time_days"] = 7
        variants.append(variant)
    return variants


def _variants_to_json(variants):
    """Normalize a list of variant dicts (from _parse_variants_from_form) for template JSON embedding."""
    out = []
    for v in variants:
        out.append(
            {
                "size": v["size"],
                "color_name": v["color_name"],
                "color_hex": v["color_hex"],
                "availability_status": v["availability_status"],
                "stock_quantity": v["stock_quantity"],
                "available_date": v["available_date"].isoformat() if v["available_date"] else "",
                "lead_time_days": v["lead_time_days"],
            }
        )
    return out


def _product_variants_to_json(product):
    out = []
    for v in product.variants:
        out.append(
            {
                "size": v.size,
                "color_name": v.color_name,
                "color_hex": v.color_hex,
                "availability_status": v.availability_status,
                "stock_quantity": v.stock_quantity,
                "available_date": v.available_date.isoformat() if v.available_date else "",
                "lead_time_days": v.lead_time_days,
            }
        )
    return out


@seller_bp.route("/products/new", methods=["GET", "POST"])
@seller_required
def product_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "")
        description = request.form.get("description", "").strip()
        base_price = request.form.get("base_price", type=float)
        image_url = request.form.get("image_url", "").strip()
        hover_image_url = request.form.get("hover_image_url", "").strip()
        is_featured = bool(request.form.get("is_featured"))

        variants = _parse_variants_from_form(request.form)

        error = None
        if not name or not category or not base_price or not image_url:
            error = "Please fill in all required product details."
        elif not variants:
            error = "Add at least one size/colour variant."

        if error:
            flash(error, "error")
            return render_template(
                "seller/product_form.html",
                product=None,
                categories=current_app.config["CATEGORIES"],
                size_order=current_app.config["SIZE_ORDER"],
                existing_variants=_variants_to_json(variants),
                form=request.form,
            )

        product = Product(
            seller_id=current_user.id,
            name=name,
            category=category,
            description=description,
            base_price=base_price,
            image_url=image_url,
            hover_image_url=hover_image_url or None,
            is_featured=is_featured,
        )
        db.session.add(product)
        db.session.flush()

        for v in variants:
            db.session.add(ProductVariant(product_id=product.id, **v))

        db.session.commit()
        flash(f"“{product.name}” is now live in your shop.", "success")
        return redirect(url_for("seller.dashboard"))

    return render_template(
        "seller/product_form.html",
        product=None,
        categories=current_app.config["CATEGORIES"],
        size_order=current_app.config["SIZE_ORDER"],
        existing_variants=[],
        form={},
    )


@seller_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@seller_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id:
        flash("Not authorized.", "error")
        return redirect(url_for("seller.dashboard"))

    if request.method == "POST":
        product.name = request.form.get("name", "").strip()
        product.category = request.form.get("category", "")
        product.description = request.form.get("description", "").strip()
        product.base_price = request.form.get("base_price", type=float)
        product.image_url = request.form.get("image_url", "").strip()
        product.hover_image_url = request.form.get("hover_image_url", "").strip() or None
        product.is_featured = bool(request.form.get("is_featured"))
        product.is_active = bool(request.form.get("is_active"))

        variants = _parse_variants_from_form(request.form)
        if not variants:
            flash("Add at least one size/colour variant.", "error")
            return render_template(
                "seller/product_form.html",
                product=product,
                categories=current_app.config["CATEGORIES"],
                size_order=current_app.config["SIZE_ORDER"],
                existing_variants=_variants_to_json(variants),
                form=request.form,
            )

        ProductVariant.query.filter_by(product_id=product.id).delete()
        for v in variants:
            db.session.add(ProductVariant(product_id=product.id, **v))

        db.session.commit()
        flash(f"“{product.name}” has been updated.", "success")
        return redirect(url_for("seller.dashboard"))

    return render_template(
        "seller/product_form.html",
        product=product,
        categories=current_app.config["CATEGORIES"],
        size_order=current_app.config["SIZE_ORDER"],
        existing_variants=_product_variants_to_json(product),
        form=None,
    )


@seller_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@seller_required
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id == current_user.id:
        db.session.delete(product)
        db.session.commit()
        flash("Product removed.", "info")
    return redirect(url_for("seller.dashboard"))


@seller_bp.route("/orders")
@seller_required
def orders():
    products = Product.query.filter_by(seller_id=current_user.id).all()
    variant_ids = [v.id for p in products for v in p.variants]
    items = []
    if variant_ids:
        items = (
            OrderItem.query.filter(OrderItem.variant_id.in_(variant_ids))
            .join(Order)
            .order_by(Order.created_at.desc())
            .all()
        )
    orders_map = {}
    for item in items:
        orders_map.setdefault(item.order, []).append(item)

    return render_template("seller/orders.html", orders_map=orders_map)

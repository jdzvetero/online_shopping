"""Seed the Veloura database with demo sellers, customers, and clothing products.

Run with:  python -m app.seed
"""
import random
from datetime import date, timedelta

from app import create_app
from app.extensions import db
from app.models import User, Product, ProductVariant

SIZES = ["XS", "S", "M", "L", "XL", "XXL"]

COLOR_PALETTE = [
    ("Royal Blue", "#4169E1"),
    ("Midnight Navy", "#1B2A4A"),
    ("Blush Pink", "#F2B8C6"),
    ("Ivory", "#F5F1E8"),
    ("Charcoal", "#36454F"),
    ("Emerald", "#2E8B57"),
    ("Sand Beige", "#D8C3A5"),
    ("Lilac Mist", "#C8A2E0"),
    ("Onyx Black", "#161616"),
    ("Cloud White", "#FAFAFA"),
    ("Rust Orange", "#B7410E"),
    ("Golden Sun", "#E8B84B"),
]

PRODUCTS = [
    ("Satin Wrap Midi Dress", "Dresses", 54.99, "A fluid satin midi with a soft wrap silhouette — dinner-date ready."),
    ("Floral Puff-Sleeve Dress", "Dresses", 42.50, "Romantic floral print with statement puff sleeves and a cinched waist."),
    ("Ribbed Bodycon Dress", "Dresses", 36.00, "Second-skin ribbed knit that moves with you, day to night."),
    ("Linen Blend Shirt Dress", "Dresses", 48.00, "Breathable linen-blend shirt dress with a relaxed, tailored fit."),
    ("Cropped Knit Cardigan", "Tops", 28.00, "Soft cropped cardigan layer with pearl buttons."),
    ("Silky Cowl-Neck Cami", "Tops", 22.00, "Liquid-drape cami with a flattering cowl neckline."),
    ("Oversized Graphic Tee", "Tops", 19.99, "Relaxed streetwear tee in heavyweight cotton."),
    ("Puff-Sleeve Blouse", "Tops", 32.00, "Structured blouse with dramatic puff sleeves and a tie neck."),
    ("High-Waist Wide Leg Trousers", "Bottoms", 39.00, "Fluid wide-leg trousers with a sculpting high waist."),
    ("Vintage Straight Jeans", "Bottoms", 44.00, "Classic straight-leg denim with a vintage wash."),
    ("Pleated Mini Skort", "Bottoms", 27.50, "Flirty pleated skort — shorts comfort, skirt style."),
    ("Faux Leather Leggings", "Bottoms", 33.00, "Sleek faux-leather leggings with a second-skin stretch fit."),
    ("Oversized Denim Jacket", "Outerwear", 58.00, "Boyfriend-fit denim jacket, pre-washed for that lived-in look."),
    ("Quilted Puffer Coat", "Outerwear", 74.99, "Lightweight quilted puffer with a longline silhouette."),
    ("Tailored Blazer", "Outerwear", 66.00, "Structured single-breasted blazer for a sharp, elevated look."),
    ("Seamless Sculpt Leggings", "Activewear", 29.99, "Buttery-soft seamless leggings built for movement."),
    ("Sports Bra + Bike Short Set", "Activewear", 34.99, "Matching studio set with breathable four-way stretch."),
    ("Zip-Through Track Jacket", "Activewear", 38.00, "Retro-stripe track jacket for warm-ups and street style."),
    ("Chain-Strap Mini Bag", "Accessories", 24.00, "Compact mini bag with a polished chain strap."),
    ("Silk-Feel Hair Scarf Set", "Accessories", 12.00, "Three-piece silky scarf set for hair and neck styling."),
]

random.seed(42)


def build_variants(seed_offset):
    """Pick 2-3 colours and up to 4 sizes, mixing in_stock / preorder / made_to_order."""
    colors = random.sample(COLOR_PALETTE, k=random.choice([2, 3]))
    sizes = random.sample(SIZES, k=4)
    sizes.sort(key=SIZES.index)

    variants = []
    i = seed_offset
    for color_name, color_hex in colors:
        for size in sizes:
            pattern = i % 3
            if pattern == 0:
                stock = random.choice([0, 2, 4, 8, 15, 25])
                variants.append(
                    dict(
                        size=size,
                        color_name=color_name,
                        color_hex=color_hex,
                        availability_status="in_stock",
                        stock_quantity=stock,
                    )
                )
            elif pattern == 1:
                ship_date = date(2026, 9, 22) + timedelta(days=random.choice([0, 7, 14, 21]))
                variants.append(
                    dict(
                        size=size,
                        color_name=color_name,
                        color_hex=color_hex,
                        availability_status="preorder",
                        available_date=ship_date,
                    )
                )
            else:
                variants.append(
                    dict(
                        size=size,
                        color_name=color_name,
                        color_hex=color_hex,
                        availability_status="made_to_order",
                        lead_time_days=random.choice([7, 10, 14]),
                    )
                )
            i += 1
    return variants


def run():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        seller_one = User(name="Amara Collins", email="seller@veloura.com", role="seller", brand_name="Amara Studio")
        seller_one.set_password("seller123")

        seller_two = User(name="Noah Reyes", email="noah@veloura.com", role="seller", brand_name="Reyes Streetwear")
        seller_two.set_password("seller123")

        customer = User(name="Jenna Parker", email="shopper@veloura.com", role="customer")
        customer.set_password("shopper123")

        db.session.add_all([seller_one, seller_two, customer])
        db.session.flush()

        sellers = [seller_one, seller_two]

        for idx, (name, category, price, description) in enumerate(PRODUCTS):
            seller = sellers[idx % len(sellers)]
            img_seed = name.lower().replace(" ", "-")
            product = Product(
                seller_id=seller.id,
                name=name,
                category=category,
                base_price=price,
                description=description,
                image_url=f"https://picsum.photos/seed/{img_seed}-a/700/900",
                hover_image_url=f"https://picsum.photos/seed/{img_seed}-b/700/900",
                is_featured=idx < 4,
            )
            db.session.add(product)
            db.session.flush()

            for v in build_variants(idx * 7):
                db.session.add(ProductVariant(product_id=product.id, **v))

        db.session.commit()

        print("Database seeded.")
        print("  Seller login:   seller@veloura.com / seller123  (Amara Studio)")
        print("  Seller login:   noah@veloura.com / seller123    (Reyes Streetwear)")
        print("  Shopper login:  shopper@veloura.com / shopper123")
        print(f"  Products created: {Product.query.count()}")
        print(f"  Variants created: {ProductVariant.query.count()}")


if __name__ == "__main__":
    run()

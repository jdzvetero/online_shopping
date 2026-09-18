# Veloura — Online Clothing Marketplace (Prototype)

A working, Shein-inspired clothing marketplace prototype: shoppers browse clothes by size/colour with live stock, pre-order or made-to-order availability, add to bag, and check out with home delivery or self pickup. Sellers get their own dashboard to list products with full size/colour/stock detail and see incoming orders.

Built with **Python (Flask)** + **SQLite** + server-rendered templates styled with a custom royal-blue glassmorphism design. No build tools, no Node — just Python.

---

## 1. Prerequisites

You only need **Python 3.10+** installed.

Check your version:

```bash
python3 --version
```

If you don't have Python, install it from [python.org/downloads](https://www.python.org/downloads/).

---

## 2. Setup (one-time)

Open a terminal in this project folder (`online_shopping/`) and run:

```bash
# 1. Create a virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows (Command Prompt / PowerShell)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create and seed the demo database (products, sellers, a shopper account)
python -m app.seed
```

You should see output confirming demo accounts and how many products/variants were created.

---

## 3. Run the app

```bash
python run.py
```

Then open **http://127.0.0.1:5000** in your browser.

To stop the server, press `Ctrl+C` in the terminal.

> Re-running `python -m app.seed` at any time wipes and re-creates the database with fresh demo data — handy if you want a clean slate.

---

## 4. Demo accounts

| Role     | Email                  | Password    |
|----------|-------------------------|-------------|
| Shopper  | shopper@veloura.com     | shopper123  |
| Seller   | seller@veloura.com      | seller123   |
| Seller   | noah@veloura.com        | seller123   |

Or click **Sign up** to create your own shopper or seller account — you choose the role at registration.

---

## 5. What you can do

### As a shopper
- Browse the full collection, filter by category, search, and sort by price.
- Open any product to select a **colour** and **size** — availability updates live:
  - **In stock** (with low-stock warnings)
  - **Pre-order** (shows the exact date it ships)
  - **Made to order** (shows how many days/weeks until it's ready)
- Check the **size guide** (bust / waist / hip chart) before choosing.
- Add items to your bag, adjust quantities, and check out.
- At checkout, choose **Home Delivery** (enter an address) or **Self Pickup** (choose a date and time).
- View your order history and confirmation details any time.

### As a seller
- See a dashboard with revenue, order count, and low/out-of-stock alerts.
- Add a new product: name, category, description, price, images.
- Add unlimited **size/colour variants** per product, each with its own availability:
  in stock (+ quantity), pre-order (+ ship date), or made to order (+ lead time).
- Edit or remove products at any time.
- View every order that includes your products.

---

## 6. Project structure

```
online_shopping/
├── run.py                  # entry point — `python run.py`
├── requirements.txt
├── app/
│   ├── __init__.py         # Flask app factory, blueprint registration
│   ├── config.py           # sizes, categories, size chart, delivery fee
│   ├── extensions.py       # SQLAlchemy + Flask-Login setup
│   ├── models.py           # User, Product, ProductVariant, Cart, Order…
│   ├── seed.py              # demo data generator
│   ├── auth/routes.py      # register / login / logout
│   ├── shop/routes.py      # browsing, product detail, cart, checkout
│   ├── seller/routes.py    # seller dashboard, product & order management
│   ├── templates/          # Jinja2 HTML templates
│   └── static/
│       ├── css/style.css   # royal-blue glassmorphism design system
│       └── js/main.js      # variant selection, animations, checkout logic
└── veloura.db               # SQLite database (created after seeding)
```

---

## 7. Notes on this prototype

- Passwords are hashed (Werkzeug), but this is a **local demo** — don't reuse real passwords.
- Checkout doesn't process real payments; placing an order just records it in the database.
- Product images are placeholder photos loaded from picsum.photos over the internet — swap `image_url` / `hover_image_url` for your own product photos any time from the seller product form.
- The database is a single SQLite file (`veloura.db`). Delete it (or re-run the seed script) to reset everything.

## 8. Natural next steps (when you're ready to go beyond a prototype)

- Real payment processing (Stripe/PayPal).
- Image uploads instead of URLs.
- Email notifications for order confirmations.
- Admin/moderation tools for multi-seller marketplaces.
- Deploying to a host (Render, Railway, Fly.io) with a production database (Postgres).

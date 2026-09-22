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
- Add a new product: name, category, description, price, and photos — **upload image files directly from your device**, or paste an image URL instead.
- Add unlimited **size/colour variants** per product, each with its own availability:
  in stock (+ quantity), pre-order (+ ship date), or made to order (+ lead time).
- Edit or remove products at any time.
- View every order that includes your products.

### Categories
Dresses, Tops, Bottoms, Outerwear, Activewear, Accessories, **Babywear**, **2 Piece Sets**, and **Tailor-Made** (fully bespoke, made-to-measure pieces — always made-to-order, sized "Custom").

---

## 6. Project structure

```
online_shopping/
├── run.py                  # entry point — `python run.py`
├── requirements.txt
├── Procfile                 # `web: gunicorn run:app` — used by most Python hosts
├── render.yaml              # one-click Render Blueprint deploy config
├── app/
│   ├── __init__.py         # Flask app factory, blueprint registration, auto-seed
│   ├── config.py           # sizes, categories, size chart, delivery fee, uploads
│   ├── extensions.py       # SQLAlchemy + Flask-Login setup
│   ├── models.py           # User, Product, ProductVariant, Cart, Order…
│   ├── seed.py              # demo data generator (CLI reseed + auto-seed on boot)
│   ├── auth/routes.py      # register / login / logout
│   ├── shop/routes.py      # browsing, product detail, cart, checkout
│   ├── seller/routes.py    # seller dashboard, product & order management, image upload
│   ├── templates/          # Jinja2 HTML templates
│   └── static/
│       ├── css/style.css   # royal-blue glassmorphism design system
│       ├── js/main.js      # variant selection, animations, checkout logic
│       └── uploads/        # seller-uploaded product photos land here
└── veloura.db               # SQLite database (created after seeding)
```

---

## 7. Notes on this prototype

- Passwords are hashed (Werkzeug), but this is a **local demo** — don't reuse real passwords.
- Checkout doesn't process real payments; placing an order just records it in the database.
- Demo products use placeholder photos loaded from picsum.photos over the internet. Sellers can upload their own photos (saved to `app/static/uploads/`) or paste an image URL from the product form.
- The database is a single SQLite file (`veloura.db`). Delete it (or re-run the seed script) to reset everything.
- The app **auto-seeds demo data on startup** if the products table is empty (set `AUTO_SEED_DEMO_DATA=false` as an env var to disable this).

---

## 8. Put it online — free, no server of your own (Render)

You don't need to own or rent a server. [Render](https://render.com) will run this app for free and give you a public link like `https://veloura-xxxx.onrender.com` that you can send to anyone.

1. **Push this project to GitHub** (if it isn't already — Render deploys from a GitHub repo).
2. Go to **[render.com](https://render.com)** and sign up (you can sign up with your GitHub account — no credit card needed for the free tier).
3. Click **New +** → **Blueprint**.
4. Connect your GitHub account if prompted, then select this repository (`online_shopping`) and the branch you want to deploy.
5. Render automatically detects the included **`render.yaml`** file in this repo and pre-fills everything (build command, start command, a generated `SECRET_KEY`, free plan). Just click **Apply** / **Create**.
6. Wait 2–5 minutes for the first build. When it's done, Render shows your live URL at the top of the service page (e.g. `https://veloura-xxxx.onrender.com`).
7. Open that link yourself once to confirm it loads, then send it to your boss. They just click it — no setup, no login required to browse.

**What to expect on the free tier:**
- The demo catalog appears automatically — no manual database setup needed, the app seeds itself on first boot.
- Free services "sleep" after ~15 minutes with no visitors. The **first** visit after sleeping takes ~30–50 seconds to wake up; after that it's fast. Let your boss know if they hit a blank/loading screen on the very first click — it'll load.
- The free tier's disk is temporary: if the service restarts (e.g. after sleeping, or after you push a new deploy), any products/orders added *during* the demo (not the seeded catalog) may reset. That's expected for a free prototype host — fine for a demo, not for real production use.
- No custom domain is required — the `onrender.com` link works as-is and is shareable immediately.

**If you'd rather not use Render:** [Railway](https://railway.app) and [PythonAnywhere](https://www.pythonanywhere.com) both offer similarly quick free/low-cost Flask hosting — the same `requirements.txt` and `run.py` work with either, just without the `render.yaml` shortcut (you'd fill in the build/start commands manually: build `pip install -r requirements.txt`, start `gunicorn run:app`).

---

## 9. Natural next steps (when you're ready to go beyond a prototype)

- Real payment processing (Stripe/PayPal).
- A persistent production database (Postgres) instead of SQLite, so data survives restarts/redeploys.
- Email notifications for order confirmations.
- Admin/moderation tools for multi-seller marketplaces.
- A custom domain and a paid Render/Railway plan (avoids the free-tier sleep delay and ephemeral disk).

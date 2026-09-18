import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'veloura.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

    SIZE_CHART = {
        "XS": {"bust": "78-81", "waist": "60-63", "hips": "85-88"},
        "S": {"bust": "82-85", "waist": "64-67", "hips": "89-92"},
        "M": {"bust": "86-90", "waist": "68-72", "hips": "93-97"},
        "L": {"bust": "91-96", "waist": "73-78", "hips": "98-103"},
        "XL": {"bust": "97-103", "waist": "79-85", "hips": "104-110"},
        "XXL": {"bust": "104-111", "waist": "86-93", "hips": "111-118"},
    }

    CATEGORIES = ["Dresses", "Tops", "Bottoms", "Outerwear", "Activewear", "Accessories"]

    DELIVERY_FEE = 5.99

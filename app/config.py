import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'veloura.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SIZE_ORDER = [
        "0-3M", "3-6M", "6-12M", "1-2Y", "2-3Y", "3-4Y",
        "XS", "S", "M", "L", "XL", "XXL", "Custom",
    ]

    SIZE_CHART = {
        "XS": {"bust": "78-81", "waist": "60-63", "hips": "85-88"},
        "S": {"bust": "82-85", "waist": "64-67", "hips": "89-92"},
        "M": {"bust": "86-90", "waist": "68-72", "hips": "93-97"},
        "L": {"bust": "91-96", "waist": "73-78", "hips": "98-103"},
        "XL": {"bust": "97-103", "waist": "79-85", "hips": "104-110"},
        "XXL": {"bust": "104-111", "waist": "86-93", "hips": "111-118"},
    }

    CATEGORIES = [
        "Dresses", "Tops", "Bottoms", "Outerwear", "Activewear",
        "Accessories", "Babywear", "2 Piece Sets", "Tailor-Made",
    ]

    # Categories where the standard adult bust/waist/hip size guide doesn't apply
    NO_SIZE_GUIDE_CATEGORIES = {"Babywear", "Tailor-Made"}

    DELIVERY_FEE = 5.99

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
    MAX_CONTENT_LENGTH = 6 * 1024 * 1024  # 6 MB per request

    AUTO_SEED_DEMO_DATA = os.environ.get("AUTO_SEED_DEMO_DATA", "true").lower() != "false"

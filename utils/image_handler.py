import os
import shutil
from PIL import Image

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")

def ensure_dirs():
    for sub in ["photos", "documents", "logo"]:
        os.makedirs(os.path.join(UPLOAD_DIR, sub), exist_ok=True)

ensure_dirs()


def save_photo(src_path: str, customer_id: int) -> str:
    """Save passport-size photo, return relative path."""
    ext  = os.path.splitext(src_path)[1].lower()
    dest = os.path.join(UPLOAD_DIR, "photos", f"cust_{customer_id}_photo{ext}")
    img  = Image.open(src_path)
    img  = img.resize((200, 200), Image.LANCZOS)
    img.save(dest)
    return dest


def save_document(src_path: str, customer_id: int) -> str:
    """Save ID document, return relative path."""
    ext  = os.path.splitext(src_path)[1].lower()
    dest = os.path.join(UPLOAD_DIR, "documents", f"cust_{customer_id}_doc{ext}")
    shutil.copy2(src_path, dest)
    return dest


def save_logo(src_path: str) -> str:
    ext  = os.path.splitext(src_path)[1].lower()
    dest = os.path.join(UPLOAD_DIR, "logo", f"bank_logo{ext}")
    shutil.copy2(src_path, dest)
    return dest


def load_image_for_display(path: str, size=(100, 100)):
    """Returns a PIL Image resized for display."""
    try:
        img = Image.open(path)
        img = img.resize(size, Image.LANCZOS)
        return img
    except Exception:
        return None
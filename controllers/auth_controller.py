import bcrypt
from models.admin    import AdminModel
from models.employee import EmployeeModel
from models.customer import CustomerModel


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def login(username: str, password: str, role: str):
    """
    Returns dict with user info + role on success, None on failure.
    role: 'admin' | 'employee' | 'customer'
    """
    if role == "admin":
        user = AdminModel.get_by_username(username)
    elif role == "employee":
        user = EmployeeModel.get_by_username(username)
    elif role == "customer":
        user = CustomerModel.get_by_username(username)
    else:
        return None

    if not user:
        return None
    if not user.get("is_active"):
        return None
    if not verify_password(password, user["password_hash"]):
        return None

    user["role"] = role
    return user


def setup_default_admin():
    """Set default admin password on first run."""
    from models.admin import AdminModel
    from config.database import Database
    import os
    from dotenv import load_dotenv
    load_dotenv()

    default_pw = os.getenv("ADMIN_DEFAULT_PASSWORD", "Admin@1234")
    hashed     = hash_password(default_pw)

    with Database() as db:
        db.execute(
            "UPDATE admins SET password_hash = %s "
            "WHERE username = 'admin' AND password_hash = 'PLACEHOLDER_WILL_BE_SET_BY_PYTHON'",
            (hashed,)
        )
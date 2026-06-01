from models.customer import CustomerModel
from controllers.auth_controller import hash_password
from utils.image_handler import save_photo, save_document


def register_customer(data: dict, photo_src=None, doc_src=None,
                       created_by_admin=None, created_by_employee=None):
    existing = CustomerModel.get_by_username(data["username"])
    if existing:
        raise ValueError("Username already exists.")

    data["password_hash"] = hash_password(data["password"])
    data.pop("password", None)

    data["created_by_admin"]    = created_by_admin
    data["created_by_employee"] = created_by_employee

    # Temporarily create to get ID
    cust_id = CustomerModel.create(data)

    # Save images if provided
    updates = {}
    if photo_src:
        updates["photo_path"] = save_photo(photo_src, cust_id)
    if doc_src:
        updates["id_document_path"] = save_document(doc_src, cust_id)

    if updates:
        cust_data = CustomerModel.get_by_id(cust_id)
        cust_data.update(updates)
        CustomerModel.update(cust_id, cust_data)

    return cust_id


def update_customer(cust_id, data, photo_src=None, doc_src=None):
    if photo_src:
        data["photo_path"] = save_photo(photo_src, cust_id)
    if doc_src:
        data["id_document_path"] = save_document(doc_src, cust_id)
    CustomerModel.update(cust_id, data)


def get_customer_full_profile(cust_id):
    from models.account     import AccountModel
    from models.transaction import TransactionModel
    from models.loan        import LoanModel

    profile = CustomerModel.get_by_id(cust_id)
    if not profile:
        return None
    profile["accounts"]     = AccountModel.get_by_customer(cust_id)
    profile["recent_txns"]  = TransactionModel.get_last_5_by_customer(cust_id)
    profile["loans"]        = LoanModel.get_by_customer(cust_id)
    return profile
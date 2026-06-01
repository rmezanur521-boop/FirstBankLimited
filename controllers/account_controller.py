from models.account     import AccountModel
from models.transaction import TransactionModel
from utils.fee_calculator import calculate_fee


def open_account(customer_id, account_type_id, initial_balance,
                 created_by_employee=None, created_by_admin=None):
    if initial_balance < 0:
        raise ValueError("Initial balance cannot be negative.")
    result = AccountModel.create(
        customer_id, account_type_id, initial_balance,
        created_by_employee, created_by_admin
    )
    if initial_balance > 0:
        TransactionModel.create({
            "from_account_id": None,
            "to_account_id"  : result["id"],
            "transaction_type": "deposit",
            "amount"         : initial_balance,
            "net_amount"     : initial_balance,
            "description"    : "Initial deposit on account opening",
            "created_by_role": "admin" if created_by_admin else "employee",
            "created_by_id"  : created_by_admin or created_by_employee
        })
    return result


def deposit(account_id, amount, performed_by_role, performed_by_id,
            description="Deposit"):
    if amount <= 0:
        raise ValueError("Amount must be positive.")
    account = AccountModel.get_by_id(account_id)
    if not account:
        raise ValueError("Account not found.")
    if account["status"] != "active":
        raise ValueError("Account is not active.")
    new_balance = float(account["balance"]) + amount
    AccountModel.update_balance(account_id, new_balance)
    return TransactionModel.create({
        "from_account_id" : None,
        "to_account_id"   : account_id,
        "transaction_type": "deposit",
        "amount"          : amount,
        "net_amount"      : amount,
        "description"     : description,
        "created_by_role" : performed_by_role,
        "created_by_id"   : performed_by_id
    })


def withdraw(account_id, amount, performed_by_role, performed_by_id,
             description="Withdrawal"):
    if amount <= 0:
        raise ValueError("Amount must be positive.")
    account = AccountModel.get_by_id(account_id)
    if not account:
        raise ValueError("Account not found.")
    if account["status"] != "active":
        raise ValueError("Account is not active.")
    if float(account["balance"]) < amount:
        raise ValueError("Insufficient balance.")
    new_balance = float(account["balance"]) - amount
    AccountModel.update_balance(account_id, new_balance)
    return TransactionModel.create({
        "from_account_id" : account_id,
        "to_account_id"   : None,
        "transaction_type": "withdraw",
        "amount"          : amount,
        "net_amount"      : amount,
        "description"     : description,
        "created_by_role" : performed_by_role,
        "created_by_id"   : performed_by_id
    })


def transfer(from_account_id, to_account_id, amount,
             performed_by_role, performed_by_id):
    if amount <= 0:
        raise ValueError("Amount must be positive.")
    if from_account_id == to_account_id:
        raise ValueError("Cannot transfer to the same account.")

    from_acc = AccountModel.get_by_id(from_account_id)
    to_acc   = AccountModel.get_by_id(to_account_id)

    if not from_acc or not to_acc:
        raise ValueError("One or both accounts not found.")
    if from_acc["status"] != "active":
        raise ValueError("Source account is not active.")
    if to_acc["status"] != "active":
        raise ValueError("Destination account is not active.")

    is_same_customer = (from_acc["customer_id"] == to_acc["customer_id"])  # fixed via account lookup
    fee_info = calculate_fee(amount, is_same_customer)

    if float(from_acc["balance"]) < amount:
        raise ValueError("Insufficient balance.")

    # Deduct full amount (including fee) from sender
    AccountModel.update_balance(
        from_account_id,
        float(from_acc["balance"]) - amount
    )
    # Credit net amount to receiver
    AccountModel.update_balance(
        to_account_id,
        float(to_acc["balance"]) + fee_info["net_amount"]
    )

    txn_type = "transfer_own" if is_same_customer else "transfer_other"
    return TransactionModel.create({
        "from_account_id" : from_account_id,
        "to_account_id"   : to_account_id,
        "transaction_type": txn_type,
        "amount"          : amount,
        "fee_percentage"  : fee_info["fee_percentage"],
        "fee_amount"      : fee_info["fee_amount"],
        "net_amount"      : fee_info["net_amount"],
        "description"     : f"Transfer ({'own' if is_same_customer else 'external'})",
        "created_by_role" : performed_by_role,
        "created_by_id"   : performed_by_id
    })
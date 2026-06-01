from models.loan    import LoanModel
from models.account import AccountModel


def calculate_emi(principal: float, annual_rate: float, months: int) -> dict:
    if months <= 0 or principal <= 0:
        raise ValueError("Invalid loan parameters.")
    if annual_rate == 0:
        emi = principal / months
    else:
        r   = annual_rate / (12 * 100)
        emi = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    emi           = round(emi, 2)
    total_payable = round(emi * months, 2)
    return {
        "emi_amount"   : emi,
        "total_payable": total_payable,
        "interest_total": round(total_payable - principal, 2)
    }


def apply_for_loan(customer_id, account_id, amount,
                   tenure_months, purpose, interest_rate=None):
    from config.database import Database
    if interest_rate is None:
        with Database() as db:
            db.execute(
                "SELECT default_loan_interest_rate FROM bank_settings LIMIT 1"
            )
            row = db.fetchone()
            interest_rate = float(row[0]) if row else 10.0

    calc = calculate_emi(amount, interest_rate, tenure_months)
    return LoanModel.apply({
        "customer_id"   : customer_id,
        "account_id"    : account_id,
        "loan_amount"   : amount,
        "interest_rate" : interest_rate,
        "tenure_months" : tenure_months,
        "emi_amount"    : calc["emi_amount"],
        "total_payable" : calc["total_payable"],
        "purpose"       : purpose
    })


def approve_loan(loan_id, admin_id):
    from models.loan import LoanModel
    from controllers.account_controller import deposit
    loan = LoanModel.get_by_id(loan_id)
    if not loan:
        raise ValueError("Loan not found.")
    if loan["status"] != "pending":
        raise ValueError("Loan is not in pending state.")
    LoanModel.approve(loan_id, admin_id)
    # Disburse amount to account
    deposit(
        loan["account_id"],
        float(loan["loan_amount"]),
        "admin", admin_id,
        description=f"Loan disbursement — {loan['loan_ref']}"
    )
    from config.database import Database
    with Database() as db:
        db.execute(
            "UPDATE loans SET status='active' WHERE id=%s", (loan_id,)
        )


def reject_loan(loan_id, admin_id, reason):
    loan = LoanModel.get_by_id(loan_id)
    if not loan:
        raise ValueError("Loan not found.")
    LoanModel.reject(loan_id, admin_id, reason)
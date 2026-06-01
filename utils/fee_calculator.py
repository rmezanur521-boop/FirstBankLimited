from config.database import Database


def get_fee_settings():
    with Database() as db:
        db.execute(
            "SELECT transfer_fee_same_customer, transfer_fee_other_customer "
            "FROM bank_settings LIMIT 1"
        )
        row = db.fetchone()
        if row:
            return {
                "same_customer": float(row[0]),
                "other_customer": float(row[1])
            }
    return {"same_customer": 0.0, "other_customer": 1.5}


def calculate_fee(amount: float, is_same_customer: bool) -> dict:
    settings   = get_fee_settings()
    fee_pct    = (settings["same_customer"] if is_same_customer
                  else settings["other_customer"])
    fee_amount = round(amount * fee_pct / 100, 2)
    net_amount = round(amount - fee_amount, 2)
    return {
        "amount"        : amount,
        "fee_percentage": fee_pct,
        "fee_amount"    : fee_amount,
        "net_amount"    : net_amount
    }
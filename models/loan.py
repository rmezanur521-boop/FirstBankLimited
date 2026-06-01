from config.database import Database


class LoanModel:

    @staticmethod
    def apply(data: dict):
        with Database() as db:
            db.execute(
                """INSERT INTO loans
                   (loan_ref, customer_id, account_id, loan_amount,
                    interest_rate, tenure_months, emi_amount,
                    total_payable, outstanding_amount, purpose)
                   VALUES ('', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id, loan_ref""",
                (
                    data["customer_id"], data["account_id"],
                    data["loan_amount"], data["interest_rate"],
                    data["tenure_months"], data["emi_amount"],
                    data["total_payable"], data["total_payable"],
                    data.get("purpose", "")
                )
            )
            row = db.fetchone()
            return {"id": row[0], "loan_ref": row[1]}

    @staticmethod
    def get_all(status=None):
        with Database() as db:
            query = """
                SELECT l.id, l.loan_ref, c.full_name, a.account_number,
                       l.loan_amount, l.interest_rate, l.tenure_months,
                       l.emi_amount, l.outstanding_amount, l.status,
                       l.applied_at, l.purpose
                FROM loans l
                JOIN customers c ON l.customer_id = c.id
                JOIN accounts  a ON l.account_id  = a.id
            """
            if status:
                query += " WHERE l.status = %s"
                db.execute(query + " ORDER BY l.applied_at DESC", (status,))
            else:
                db.execute(query + " ORDER BY l.applied_at DESC")
            rows = db.fetchall()
            keys = [
                "id","loan_ref","customer_name","account_number",
                "loan_amount","interest_rate","tenure_months",
                "emi_amount","outstanding_amount","status",
                "applied_at","purpose"
            ]
            return [dict(zip(keys, r)) for r in rows]

    @staticmethod
    def get_by_customer(customer_id: int):
        with Database() as db:
            db.execute(
                """SELECT l.id, l.loan_ref, a.account_number,
                          l.loan_amount, l.interest_rate, l.tenure_months,
                          l.emi_amount, l.total_payable, l.amount_paid,
                          l.outstanding_amount, l.status, l.applied_at
                   FROM loans l
                   JOIN accounts a ON l.account_id = a.id
                   WHERE l.customer_id = %s ORDER BY l.applied_at DESC""",
                (customer_id,)
            )
            rows = db.fetchall()
            keys = [
                "id","loan_ref","account_number","loan_amount",
                "interest_rate","tenure_months","emi_amount",
                "total_payable","amount_paid","outstanding_amount",
                "status","applied_at"
            ]
            return [dict(zip(keys, r)) for r in rows]

    @staticmethod
    def approve(loan_id: int, admin_id: int):
        with Database() as db:
            db.execute(
                """UPDATE loans SET status='approved',
                   approved_at=CURRENT_TIMESTAMP, approved_by=%s
                   WHERE id=%s""",
                (admin_id, loan_id)
            )

    @staticmethod
    def reject(loan_id: int, admin_id: int, reason: str):
        with Database() as db:
            db.execute(
                """UPDATE loans SET status='rejected',
                   approved_by=%s, rejection_reason=%s
                   WHERE id=%s""",
                (admin_id, reason, loan_id)
            )

    @staticmethod
    def get_by_id(loan_id: int):
        with Database() as db:
            db.execute(
                """SELECT l.id, l.loan_ref, l.customer_id, c.full_name,
                          l.account_id, a.account_number,
                          l.loan_amount, l.interest_rate, l.tenure_months,
                          l.emi_amount, l.total_payable, l.amount_paid,
                          l.outstanding_amount, l.purpose, l.status,
                          l.applied_at, l.rejection_reason
                   FROM loans l
                   JOIN customers c ON l.customer_id = c.id
                   JOIN accounts  a ON l.account_id  = a.id
                   WHERE l.id = %s""",
                (loan_id,)
            )
            row = db.fetchone()
            if row:
                keys = [
                    "id","loan_ref","customer_id","customer_name",
                    "account_id","account_number","loan_amount",
                    "interest_rate","tenure_months","emi_amount",
                    "total_payable","amount_paid","outstanding_amount",
                    "purpose","status","applied_at","rejection_reason"
                ]
                return dict(zip(keys, row))
            return None

    @staticmethod
    def record_repayment(loan_id, amount_paid, transaction_id=None):
        with Database() as db:
            db.execute(
                "INSERT INTO loan_repayments (loan_id, amount_paid, transaction_id) "
                "VALUES (%s, %s, %s)",
                (loan_id, amount_paid, transaction_id)
            )
            db.execute(
                """UPDATE loans SET
                   amount_paid = amount_paid + %s,
                   outstanding_amount = outstanding_amount - %s
                   WHERE id = %s""",
                (amount_paid, amount_paid, loan_id)
            )
            db.execute(
                "UPDATE loans SET status='closed' "
                "WHERE id=%s AND outstanding_amount <= 0",
                (loan_id,)
            )
from config.database import Database


class TransactionModel:

    @staticmethod
    def create(data: dict):
        with Database() as db:
            db.execute(
                """INSERT INTO transactions
                   (transaction_ref, from_account_id, to_account_id,
                    transaction_type, amount, fee_amount, fee_percentage,
                    net_amount, description, status,
                    created_by_role, created_by_id)
                   VALUES ('', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                   RETURNING id, transaction_ref""",
                (
                    data.get("from_account_id"), data.get("to_account_id"),
                    data["transaction_type"], data["amount"],
                    data.get("fee_amount", 0), data.get("fee_percentage", 0),
                    data["net_amount"], data.get("description", ""),
                    data.get("status", "completed"),
                    data.get("created_by_role"), data.get("created_by_id")
                )
            )
            row = db.fetchone()
            return {"id": row[0], "transaction_ref": row[1]}

    @staticmethod
    def get_by_account(account_id: int, limit=50):
        with Database() as db:
            db.execute(
                """SELECT t.id, t.transaction_ref, t.transaction_type,
                          t.amount, t.fee_amount, t.net_amount,
                          t.description, t.status, t.created_at,
                          fa.account_number AS from_acc,
                          ta.account_number AS to_acc
                   FROM transactions t
                   LEFT JOIN accounts fa ON t.from_account_id = fa.id
                   LEFT JOIN accounts ta ON t.to_account_id   = ta.id
                   WHERE t.from_account_id = %s OR t.to_account_id = %s
                   ORDER BY t.created_at DESC LIMIT %s""",
                (account_id, account_id, limit)
            )
            rows = db.fetchall()
            keys = [
                "id","transaction_ref","transaction_type","amount",
                "fee_amount","net_amount","description","status",
                "created_at","from_acc","to_acc"
            ]
            return [dict(zip(keys, r)) for r in rows]

    @staticmethod
    def get_all(limit=200):
        with Database() as db:
            db.execute(
                """SELECT t.id, t.transaction_ref, t.transaction_type,
                          t.amount, t.fee_amount, t.net_amount,
                          t.status, t.created_at,
                          fa.account_number AS from_acc,
                          ta.account_number AS to_acc
                   FROM transactions t
                   LEFT JOIN accounts fa ON t.from_account_id = fa.id
                   LEFT JOIN accounts ta ON t.to_account_id   = ta.id
                   ORDER BY t.created_at DESC LIMIT %s""",
                (limit,)
            )
            rows = db.fetchall()
            keys = [
                "id","transaction_ref","transaction_type","amount",
                "fee_amount","net_amount","status","created_at",
                "from_acc","to_acc"
            ]
            return [dict(zip(keys, r)) for r in rows]

    @staticmethod
    def get_last_5_by_customer(customer_id: int):
        with Database() as db:
            db.execute(
                """SELECT t.transaction_ref, t.transaction_type,
                          t.amount, t.net_amount, t.created_at,
                          fa.account_number AS from_acc,
                          ta.account_number AS to_acc
                   FROM transactions t
                   LEFT JOIN accounts fa ON t.from_account_id = fa.id
                   LEFT JOIN accounts ta ON t.to_account_id   = ta.id
                   WHERE fa.customer_id = %s OR ta.customer_id = %s
                   ORDER BY t.created_at DESC LIMIT 5""",
                (customer_id, customer_id)
            )
            rows = db.fetchall()
            keys = [
                "transaction_ref","transaction_type","amount",
                "net_amount","created_at","from_acc","to_acc"
            ]
            return [dict(zip(keys, r)) for r in rows]

    @staticmethod
    def search_by_date_and_amount(account_id, from_date=None,
                                   to_date=None, amount=None):
        with Database() as db:
            query = """
                SELECT t.id, t.transaction_ref, t.transaction_type,
                       t.amount, t.fee_amount, t.net_amount,
                       t.status, t.created_at
                FROM transactions t
                WHERE (t.from_account_id = %s OR t.to_account_id = %s)
            """
            params = [account_id, account_id]
            if from_date:
                query += " AND DATE(t.created_at) >= %s"
                params.append(from_date)
            if to_date:
                query += " AND DATE(t.created_at) <= %s"
                params.append(to_date)
            if amount:
                query += " AND t.amount = %s"
                params.append(amount)
            query += " ORDER BY t.created_at DESC"
            db.execute(query, params)
            rows = db.fetchall()
            keys = [
                "id","transaction_ref","transaction_type","amount",
                "fee_amount","net_amount","status","created_at"
            ]
            return [dict(zip(keys, r)) for r in rows]
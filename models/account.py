from config.database import Database


class AccountModel:

    @staticmethod
    def get_all():
        with Database() as db:
            db.execute(
                "SELECT a.id, a.account_number, c.full_name, "
                "at.type_name, a.balance, a.status, a.opened_at "
                "FROM accounts a "
                "JOIN customers c ON a.customer_id = c.id "
                "JOIN account_types at ON a.account_type_id = at.id "
                "ORDER BY a.id DESC"
            )
            rows = db.fetchall()
            return [
                {
                    "id": r[0], "account_number": r[1], "customer_name": r[2],
                    "account_type": r[3], "balance": r[4],
                    "status": r[5], "opened_at": r[6]
                } for r in rows
            ]

    @staticmethod
    def get_by_customer(customer_id: int):
        with Database() as db:
            db.execute(
                "SELECT a.id, a.account_number, at.type_name, a.balance, a.status "
                "FROM accounts a "
                "JOIN account_types at ON a.account_type_id = at.id "
                "WHERE a.customer_id = %s ORDER BY a.id",
                (customer_id,)
            )
            rows = db.fetchall()
            return [
                {
                    "id": r[0], "account_number": r[1],
                    "account_type": r[2], "balance": r[3], "status": r[4]
                } for r in rows
            ]

    @staticmethod
    def get_by_id(account_id: int):
        with Database() as db:
            db.execute(
                "SELECT a.id, a.account_number, a.customer_id, c.full_name, "
                "at.type_name, a.balance, a.status, a.opened_at "
                "FROM accounts a "
                "JOIN customers c ON a.customer_id = c.id "
                "JOIN account_types at ON a.account_type_id = at.id "
                "WHERE a.id = %s",
                (account_id,)
            )
            row = db.fetchone()
            if row:
                return {
                    "id": row[0], "account_number": row[1],
                    "customer_id": row[2], "customer_name": row[3],
                    "account_type": row[4], "balance": row[5],
                    "status": row[6], "opened_at": row[7]
                }
            return None

    @staticmethod
    def get_by_account_number(acc_no: str):
        with Database() as db:
            db.execute(
                "SELECT a.id, a.account_number, a.customer_id, c.full_name, "
                "at.type_name, a.balance, a.status "
                "FROM accounts a "
                "JOIN customers c ON a.customer_id = c.id "
                "JOIN account_types at ON a.account_type_id = at.id "
                "WHERE a.account_number = %s",
                (acc_no,)
            )
            row = db.fetchone()
            if row:
                return {
                    "id": row[0], "account_number": row[1],
                    "customer_id": row[2], "customer_name": row[3],
                    "account_type": row[4], "balance": row[5], "status": row[6]
                }
            return None

    @staticmethod
    def create(customer_id, account_type_id, initial_balance,
               created_by_employee=None, created_by_admin=None):
        with Database() as db:
            db.execute(
                "INSERT INTO accounts (account_number, customer_id, account_type_id, "
                "balance, created_by_employee, created_by_admin) "
                "VALUES ('', %s, %s, %s, %s, %s) RETURNING id, account_number",
                (customer_id, account_type_id, initial_balance,
                 created_by_employee, created_by_admin)
            )
            row = db.fetchone()
            return {"id": row[0], "account_number": row[1]}

    @staticmethod
    def update_balance(account_id: int, new_balance: float):
        with Database() as db:
            db.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_balance, account_id)
            )

    @staticmethod
    def update_status(account_id: int, status: str):
        with Database() as db:
            db.execute(
                "UPDATE accounts SET status = %s WHERE id = %s",
                (status, account_id)
            )

    @staticmethod
    def get_account_types():
        with Database() as db:
            db.execute("SELECT id, type_name, min_balance FROM account_types")
            rows = db.fetchall()
            return [
                {"id": r[0], "type_name": r[1], "min_balance": r[2]}
                for r in rows
            ]
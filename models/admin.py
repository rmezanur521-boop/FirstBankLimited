from config.database import Database


class AdminModel:

    @staticmethod
    def get_by_username(username: str):
        with Database() as db:
            db.execute(
                "SELECT id, full_name, username, password_hash, email, phone, is_active "
                "FROM admins WHERE username = %s",
                (username,)
            )
            row = db.fetchone()
            if row:
                return {
                    "id": row[0], "full_name": row[1], "username": row[2],
                    "password_hash": row[3], "email": row[4],
                    "phone": row[5], "is_active": row[6]
                }
            return None

    @staticmethod
    def get_by_id(admin_id: int):
        with Database() as db:
            db.execute(
                "SELECT id, full_name, username, email, phone, is_active "
                "FROM admins WHERE id = %s",
                (admin_id,)
            )
            row = db.fetchone()
            if row:
                return {
                    "id": row[0], "full_name": row[1], "username": row[2],
                    "email": row[3], "phone": row[4], "is_active": row[5]
                }
            return None

    @staticmethod
    def update_password(admin_id: int, new_hash: str):
        with Database() as db:
            db.execute(
                "UPDATE admins SET password_hash = %s WHERE id = %s",
                (new_hash, admin_id)
            )

    @staticmethod
    def get_dashboard_stats():
        with Database() as db:
            stats = {}
            db.execute("SELECT COUNT(*) FROM customers WHERE is_active = TRUE")
            stats["total_customers"] = db.fetchone()[0]

            db.execute("SELECT COUNT(*) FROM accounts WHERE status = 'active'")
            stats["total_accounts"] = db.fetchone()[0]

            db.execute("SELECT COALESCE(SUM(balance), 0) FROM accounts WHERE status = 'active'")
            stats["total_balance"] = db.fetchone()[0]

            db.execute(
                "SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM transactions "
                "WHERE DATE(created_at) = CURRENT_DATE"
            )
            row = db.fetchone()
            stats["today_txn_amount"] = row[0]
            stats["today_txn_count"]  = row[1]

            db.execute("SELECT COUNT(*) FROM loans WHERE status = 'pending'")
            stats["pending_loans"] = db.fetchone()[0]

            db.execute(
                "SELECT COUNT(*) FROM loans WHERE status IN ('active','approved')"
            )
            stats["active_loans"] = db.fetchone()[0]

            db.execute(
                "SELECT COALESCE(SUM(loan_amount),0) FROM loans WHERE status='active'"
            )
            stats["total_disbursed"] = db.fetchone()[0]

            return stats
from config.database import Database


class EmployeeModel:

    @staticmethod
    def get_by_username(username: str):
        with Database() as db:
            db.execute(
                "SELECT id, full_name, username, password_hash, email, phone, "
                "designation, is_active FROM employees WHERE username = %s",
                (username,)
            )
            row = db.fetchone()
            if row:
                return {
                    "id": row[0], "full_name": row[1], "username": row[2],
                    "password_hash": row[3], "email": row[4], "phone": row[5],
                    "designation": row[6], "is_active": row[7]
                }
            return None

    @staticmethod
    def get_all():
        with Database() as db:
            db.execute(
                "SELECT id, full_name, username, email, phone, designation, "
                "is_active, created_at FROM employees ORDER BY id DESC"
            )
            rows = db.fetchall()
            return [
                {
                    "id": r[0], "full_name": r[1], "username": r[2],
                    "email": r[3], "phone": r[4], "designation": r[5],
                    "is_active": r[6], "created_at": r[7]
                } for r in rows
            ]

    @staticmethod
    def create(full_name, username, password_hash, email, phone,
               designation, created_by):
        with Database() as db:
            db.execute(
                "INSERT INTO employees (full_name, username, password_hash, "
                "email, phone, designation, created_by) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (full_name, username, password_hash, email,
                 phone, designation, created_by)
            )
            return db.fetchone()[0]

    @staticmethod
    def update(emp_id, full_name, email, phone, designation, is_active):
        with Database() as db:
            db.execute(
                "UPDATE employees SET full_name=%s, email=%s, phone=%s, "
                "designation=%s, is_active=%s WHERE id=%s",
                (full_name, email, phone, designation, is_active, emp_id)
            )

    @staticmethod
    def delete(emp_id):
        with Database() as db:
            db.execute("DELETE FROM employees WHERE id = %s", (emp_id,))

    @staticmethod
    def get_by_id(emp_id):
        with Database() as db:
            db.execute(
                "SELECT id, full_name, username, email, phone, "
                "designation, is_active FROM employees WHERE id = %s",
                (emp_id,)
            )
            row = db.fetchone()
            if row:
                return {
                    "id": row[0], "full_name": row[1], "username": row[2],
                    "email": row[3], "phone": row[4],
                    "designation": row[5], "is_active": row[6]
                }
            return None
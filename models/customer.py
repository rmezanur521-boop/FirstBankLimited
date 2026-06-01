from config.database import Database


class CustomerModel:

    @staticmethod
    def get_by_username(username: str):
        with Database() as db:
            db.execute(
                "SELECT id, full_name, username, password_hash, phone, "
                "email, is_active FROM customers WHERE username = %s",
                (username,)
            )
            row = db.fetchone()
            if row:
                return {
                    "id": row[0], "full_name": row[1], "username": row[2],
                    "password_hash": row[3], "phone": row[4],
                    "email": row[5], "is_active": row[6]
                }
            return None

    @staticmethod
    def get_all():
        with Database() as db:
            db.execute(
                "SELECT c.id, c.full_name, c.username, c.phone, c.email, "
                "c.is_active, c.kyc_verified, c.created_at, "
                "COUNT(a.id) AS account_count "
                "FROM customers c "
                "LEFT JOIN accounts a ON a.customer_id = c.id "
                "GROUP BY c.id ORDER BY c.id DESC"
            )
            rows = db.fetchall()
            return [
                {
                    "id": r[0], "full_name": r[1], "username": r[2],
                    "phone": r[3], "email": r[4], "is_active": r[5],
                    "kyc_verified": r[6], "created_at": r[7],
                    "account_count": r[8]
                } for r in rows
            ]

    @staticmethod
    def get_by_id(cust_id: int):
        with Database() as db:
            db.execute(
                "SELECT id, full_name, username, father_name, mother_name, "
                "date_of_birth, gender, phone, email, address, city, "
                "id_type, id_number, id_document_path, photo_path, "
                "kyc_verified, is_active, created_at "
                "FROM customers WHERE id = %s",
                (cust_id,)
            )
            row = db.fetchone()
            if row:
                keys = [
                    "id","full_name","username","father_name","mother_name",
                    "date_of_birth","gender","phone","email","address","city",
                    "id_type","id_number","id_document_path","photo_path",
                    "kyc_verified","is_active","created_at"
                ]
                return dict(zip(keys, row))
            return None

    @staticmethod
    def create(data: dict):
        with Database() as db:
            db.execute(
                """INSERT INTO customers
                   (full_name, username, password_hash, father_name, mother_name,
                    date_of_birth, gender, phone, email, address, city,
                    id_type, id_number, id_document_path, photo_path,
                    created_by_employee, created_by_admin)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   RETURNING id""",
                (
                    data["full_name"], data["username"], data["password_hash"],
                    data.get("father_name"), data.get("mother_name"),
                    data.get("date_of_birth"), data.get("gender"),
                    data["phone"], data.get("email"), data.get("address"),
                    data.get("city"), data.get("id_type"), data.get("id_number"),
                    data.get("id_document_path"), data.get("photo_path"),
                    data.get("created_by_employee"), data.get("created_by_admin")
                )
            )
            return db.fetchone()[0]

    @staticmethod
    def update(cust_id, data: dict):
        with Database() as db:
            db.execute(
                """UPDATE customers SET
                   full_name=%s, father_name=%s, mother_name=%s,
                   date_of_birth=%s, gender=%s, phone=%s, email=%s,
                   address=%s, city=%s, id_type=%s, id_number=%s,
                   kyc_verified=%s, is_active=%s
                   WHERE id=%s""",
                (
                    data["full_name"], data.get("father_name"),
                    data.get("mother_name"), data.get("date_of_birth"),
                    data.get("gender"), data["phone"], data.get("email"),
                    data.get("address"), data.get("city"),
                    data.get("id_type"), data.get("id_number"),
                    data.get("kyc_verified", False),
                    data.get("is_active", True), cust_id
                )
            )

    @staticmethod
    def delete(cust_id: int):
        with Database() as db:
            db.execute("DELETE FROM customers WHERE id = %s", (cust_id,))

    @staticmethod
    def search(keyword: str):
        with Database() as db:
            db.execute(
                "SELECT id, full_name, username, phone, email, is_active "
                "FROM customers WHERE full_name ILIKE %s OR phone ILIKE %s "
                "OR username ILIKE %s ORDER BY full_name",
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
            )
            rows = db.fetchall()
            return [
                {
                    "id": r[0], "full_name": r[1], "username": r[2],
                    "phone": r[3], "email": r[4], "is_active": r[5]
                } for r in rows
            ]
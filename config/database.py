import psycopg2
from psycopg2 import pool, OperationalError
from dotenv import load_dotenv
import os

load_dotenv()

class DatabaseConfig:
    _connection_pool = None

    DB_CONFIG = {
        "host"    : os.getenv("DB_HOST", "localhost"),
        "port"    : os.getenv("DB_PORT", 5432),
        "database": os.getenv("DB_NAME", "first_bank_limited"),
        "user"    : os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
    }

    @classmethod
    def initialize_pool(cls):
        try:
            cls._connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                **cls.DB_CONFIG
            )
            print("[DB] Connection pool initialized successfully.")
        except OperationalError as e:
            print(f"[DB ERROR] Could not initialize pool: {e}")
            raise

    @classmethod
    def get_connection(cls):
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool.getconn()

    @classmethod
    def release_connection(cls, conn):
        if cls._connection_pool and conn:
            cls._connection_pool.putconn(conn)

    @classmethod
    def close_all(cls):
        if cls._connection_pool:
            cls._connection_pool.closeall()
            print("[DB] All connections closed.")


class Database:
    """Context manager for safe DB operations."""

    def __init__(self):
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn   = DatabaseConfig.get_connection()
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
            print(f"[DB ROLLBACK] {exc_val}")
        else:
            self.conn.commit()
        self.cursor.close()
        DatabaseConfig.release_connection(self.conn)

    def execute(self, query, params=None):
        self.cursor.execute(query, params or ())

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def rowcount(self):
        return self.cursor.rowcount
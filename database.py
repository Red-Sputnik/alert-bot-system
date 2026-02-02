import sqlite3
from typing import Optional

class Database:
    def __init__(self, path: str = "users.db"):
        self.path = path
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _create_table(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL
                )
            """)
    def add_user(self, telegram_id: int, name: str, phone: str):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO users (telegram_id, name, phone)
                VALUES (?, ?, ?)
                """,
                (telegram_id, name, phone)
            )

    def get_user(self, telegram_id: int) -> Optional[tuple]:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT telegram_id, name, phone FROM users WHERE telegram_id = ?",
                (telegram_id,)
            )
            return cursor.fetchone()

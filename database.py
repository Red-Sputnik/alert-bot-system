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
                    phone TEXT NOT NULL,
                    status TEXT,
                    latitude REAL,
                    longitude REAL
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

    def get_all_users(self) -> list[tuple]:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT telegram_id FROM users"
            )
            return cursor.fetchall()
    
    def update_status(self, telegram_id: int, status: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET status = ? WHERE telegram_id = ?", 
                (status, telegram_id)
            )

    def update_location(self, telegram_id: int, latitude: float, longitude: float):
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE users
                SET latitude = ?, longitude = ?
                WHERE telegram_id = ?
                """,
                (latitude, longitude, telegram_id)
            )

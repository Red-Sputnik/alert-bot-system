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
                    region TEXT,
                    status TEXT,
                    latitude REAL,
                    longitude REAL
                )
            """)
    def add_user(self, telegram_id: int, name: str, phone: str):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users (telegram_id, name, phone)
                VALUES (?, ?, ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    name = excluded.name,
                    phone = excluded.phone
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

    def update_region(self, telegram_id: int, region: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET region = ? WHERE telegram_id = ?",
                (region, telegram_id)
            )

    def count_users(self) -> int:
        with self._connect() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]

    def count_by_status(self) -> dict:
        with self._connect() as conn:
            cursor = conn.execute("""
            SELECT status, COUNT(*) 
            FROM users 
            GROUP BY status
        """)
        return {row[0]: row[1] for row in cursor.fetchall()}

    def count_with_location(self) -> int:
        with self._connect() as conn:
            cursor = conn.execute("""
            SELECT COUNT(*) 
            FROM users 
            WHERE latitude IS NOT NULL 
              AND longitude IS NOT NULL
        """)
        return cursor.fetchone()[0]

    def user_exists(self, telegram_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM users WHERE telegram_id = ?",
                (telegram_id,)
            )
            return cursor.fetchone() is not None

    def get_users_by_regions(self, regions: list[str]) -> list[int]:
        placeholders = ",".join("?" for _ in regions)

        query = f"""
            SELECT telegram_id
            FROM users
            WHERE region IN ({placeholders})
        """

        with self._connect() as conn:
            cursor = conn.execute(query, regions)
            return [row[0] for row in cursor.fetchall()]


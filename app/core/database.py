import sqlite3
from contextlib import contextmanager
from typing import Generator

DB_PATH = "trademark.db"

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    데이터베이스를 연결해주는 매니저
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_db():
    """
    데이터베이스를 초기화하는 함수
    """
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trademarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_number TEXT UNIQUE NOT NULL,
            name_kr TEXT,
            name_en TEXT,
            status TEXT,
            app_date TEXT,
            codes TEXT,
            chosung TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_chosung
        ON trademarks(chosung)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_status
        ON trademarks(status)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_app_date
        ON trademarks(app_date)
        """)

        conn.commit()
        print("데이터베이스 초기화.")

def get_db_status() -> dict:
    """
    데이터베이스 상태를 조회하는 함수
    """
    with get_db() as conn:
        cursor = conn.cursor()
        total = cursor.execute("SELECT COUNT(*) FROM trademarks").fetchone()[0]
        return {"total": total}
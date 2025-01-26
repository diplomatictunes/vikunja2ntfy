import aiosqlite
import logging

SQLITE_DB_PATH = "./data/reminders.db"

async def initialize_databases():
    """Initialize SQLite database and tables."""
    try:
        async with aiosqlite.connect(SQLITE_DB_PATH) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS task_reminders (
                    id INTEGER PRIMARY KEY,
                    task_id INTEGER NOT NULL,
                    task_name TEXT NOT NULL,
                    description TEXT,
                    reminder TEXT NOT NULL,
                    created TEXT NOT NULL,
                    relative_period INTEGER,
                    relative_to TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS past_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT NOT NULL,
                    reminder TEXT NOT NULL,
                    description TEXT,
                    moved_at TEXT NOT NULL
                )
            """)
            await db.commit()
            logging.info("SQLite database initialized.")
    except Exception as e:
        logging.error(f"Error initializing SQLite: {e}")

import psycopg2
import json
import logging
import asyncio
import os
import re
import aiosqlite
from database import SQLITE_DB_PATH  # Shared SQLite database path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# PostgreSQL connection settings (configurable via environment variables)
PG_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "dbname": os.getenv("DB_NAME", "vikunja"),
    "user": os.getenv("DB_USER", "vikunja"),
    "password": os.getenv("DB_PASSWORD", "vikunja"),
}

def strip_html_tags(text):
    """
    Remove specific HTML tags from the input text (e.g., <p> and </p>).
    """
    return re.sub(r"</?p>", "", text, flags=re.IGNORECASE).strip()

# Handle PostgreSQL notifications
async def handle_notification(payload):
    """
    Reflect PostgreSQL operations (INSERT, DELETE, UPDATE) in the SQLite database.
    """
    try:
        operation = payload.get("operation")
        changed_row = payload.get("changed_row")
        task = payload.get("task")

        if not changed_row:
            logging.warning(f"Notification payload missing 'changed_row': {payload}")
            return

        # Extract task details
        task_name = task.get("title", "Unknown Task") if task else "Unknown Task"
        description = strip_html_tags(task.get("description", "")) if task else ""

        async with aiosqlite.connect(SQLITE_DB_PATH) as db:
            if operation == "INSERT":
                await db.execute("""
                    INSERT OR IGNORE INTO task_reminders (id, task_id, task_name, description, reminder, created, relative_period, relative_to)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    changed_row["id"],
                    changed_row["task_id"],
                    task_name,
                    description,
                    changed_row["reminder"],
                    changed_row["created"],
                    changed_row.get("relative_period"),
                    changed_row.get("relative_to"),
                ))
                logging.info(f"Inserted into SQLite: {changed_row}")

            elif operation == "DELETE":
                await db.execute("""
                    DELETE FROM task_reminders WHERE id = ?
                """, (changed_row["id"],))
                logging.info(f"Deleted from SQLite: {changed_row}")

            elif operation == "UPDATE":
                await db.execute("""
                    UPDATE task_reminders
                    SET task_id = ?, task_name = ?, description = ?, reminder = ?, created = ?, relative_period = ?, relative_to = ?
                    WHERE id = ?
                """, (
                    changed_row["task_id"],
                    task_name,
                    description,
                    changed_row["reminder"],
                    changed_row["created"],
                    changed_row.get("relative_period"),
                    changed_row.get("relative_to"),
                    changed_row["id"],
                ))
                logging.info(f"Updated in SQLite: {changed_row}")

            else:
                logging.warning(f"Unhandled operation '{operation}': {payload}")

            await db.commit()

    except Exception as e:
        logging.error(f"Error processing notification payload: {e}\nPayload: {payload}")

# Listen for PostgreSQL notifications
async def listen_notifications():
    """
    Listen for PostgreSQL notifications on a specific channel.
    """
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute("LISTEN task_reminders_changes;")
        logging.info("Listening for PostgreSQL notifications...")

        while True:
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop(0)
                try:
                    logging.info(f"Notification received from PostgreSQL: {notify.payload}")
                    payload = json.loads(notify.payload)
                    logging.info(f"Parsed notification payload: {payload}")
                    await handle_notification(payload)
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decode error: {e} | Raw payload: {notify.payload}")
                except Exception as e:
                    logging.error(f"Error handling notification: {e}")
            await asyncio.sleep(1)

    except Exception as e:
        logging.error(f"Error listening for notifications: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("PostgreSQL connection closed.")

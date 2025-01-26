import asyncio
import aiosqlite
import requests
import logging
from datetime import datetime, timezone
from database import SQLITE_DB_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

NTFY_URL = "https://ntfy.diplomatictunes.com/vikunja"

async def check_and_send_notifications():
    """Check SQLite for due reminders and send notifications."""
    try:
        while True:
            now = datetime.now(timezone.utc).isoformat(timespec="seconds")
            logging.info(f"Checking for due reminders at {now}...")

            async with aiosqlite.connect(SQLITE_DB_PATH) as db:
                # Log the database query
                logging.info("Querying SQLite for reminders due now or earlier...")
                async with db.execute("""
                    SELECT id, task_name, reminder, description
                    FROM task_reminders
                    WHERE reminder <= ?
                """, (now,)) as cursor:
                    reminders = await cursor.fetchall()
                    logging.info(f"Found {len(reminders)} reminders to process.")

                    for reminder in reminders:
                        reminder_id, task_name, reminder_time, description = reminder
                        logging.info(f"Processing reminder: ID={reminder_id}, Task={task_name}, Reminder Time={reminder_time}")

                        try:
                            # Log the HTTP request details
                            post_data = description or ""
                            post_headers = {
			        "Title": task_name,
                                "Tags": "llama",
                                "Click": "https://todo.craig.wiki"
                            }
                            logging.info(f"Sending POST request to {NTFY_URL} with data: '{post_data}' and headers: {post_headers}")

                            # Send the notification
                            response = requests.post(
                                NTFY_URL,
                                data=post_data,
                                headers=post_headers
                            )
                            # Log the response details
                            if response.status_code == 200:
                                logging.info(f"Notification successfully sent for task: {task_name} | Response: {response.text}")
                            else:
                                logging.error(f"Failed to send notification for task: {task_name} | Status: {response.status_code} | Response: {response.text}")
                        except Exception as e:
                            logging.error(f"Error sending notification for task: {task_name} | Error: {e}")

                        # Move the reminder to past_reminders
                        moved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
                        logging.info(f"Moving reminder ID={reminder_id} to past_reminders at {moved_at}.")
                        await db.execute("""
                            INSERT INTO past_reminders (task_name, reminder, description, moved_at)
                            VALUES (?, ?, ?, ?)
                        """, (task_name, reminder_time, description, moved_at))
                        await db.execute("DELETE FROM task_reminders WHERE id = ?", (reminder_id,))
                        await db.commit()
                        logging.info(f"Reminder ID={reminder_id} successfully moved to past_reminders.")

            logging.info("Finished processing reminders. Waiting for the next check...")
            await asyncio.sleep(60)
    except Exception as e:
        logging.error(f"Error in notification task: {e}")

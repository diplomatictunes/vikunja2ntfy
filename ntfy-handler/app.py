from fastapi import FastAPI
import asyncio
from listen import listen_notifications
from notify import check_and_send_notifications
from database import initialize_databases

app = FastAPI(title="Notification Handler")

@app.on_event("startup")
async def startup():
    """Run database initialization and background tasks."""
    await initialize_databases()  # Shared database setup
    asyncio.create_task(listen_notifications())  # Start the listener
    asyncio.create_task(check_and_send_notifications())  # Start the notifier

@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Notification Handler is running"}

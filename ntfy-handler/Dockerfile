# Use a minimal Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy only essential files to leverage Docker layer caching
COPY requirements.txt requirements.txt
COPY app.py app.py
COPY database.py database.py
COPY listen.py listen.py
COPY notify.py notify.py
COPY .dockerignore .dockerignore

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directory for SQLite database (persistent storage within container)
RUN mkdir -p /app/data

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI application with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

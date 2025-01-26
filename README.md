# Vikunja Notification Handler

---

## Prerequisites

Ensure you have the following installed before running the project:

- Docker
- Docker Compose
- Python 3.8+ (for local development)

---

## Setup and Usage

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

### 2. Configuration

Edit `config/config.yml` to set up your environment. Here's an example:

```yaml
vikunja:
  url: "http://<vikunja-domain>"
  api_token: "<your-vikunja-api-token>"
ntfy:
  url: "https://<ntfy-domain>"
database:
  type: "postgresql"
  host: "db"
  port: 5432
  name: "vikunja"
  user: "vikunja"
  password: "<your-database-password>"
```

### 3. Start the Service

Use Docker Compose to build and start the services:

```bash
docker compose up --build
```

### 4. Access the Services

- **Vikunja**: Available at `http://localhost:8080` (or the configured port)
- **PostgreSQL**: Exposed on `localhost:5432` for debugging (configured in `compose.yaml`)
- **Notification Handler**: Automatically listens for Vikunja updates and sends notifications to Ntfy

---

## Development

To run the notification handler locally:

### 1. Set up a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r ntfy-handler/requirements.txt
```

### 3. Run the application

```bash
python ntfy-handler/app.py
```

---

## Debugging and Querying Databases

### PostgreSQL Database

The `compose.yaml` file automatically sets up a PostgreSQL container for Vikunja. For manual debugging:

1. Connect to the PostgreSQL database:

   ```bash
   docker exec -it <postgres-container-name> psql -U vikunja -d vikunja
   ```

2. Run queries to verify data:

   ```sql
   SELECT * FROM reminders;
   ```

### SQLite Database

The `reminders.db` file is automatically set up by `database.py`. For manual debugging:

1. Connect to the SQLite database:

   ```bash
   sqlite3 <path/to/reminders.db>
   ```

2. Turn on headers and check tables (optional):

   ```sql
   .headers yes
   .tables
   .schema
   ```

3. Query tables:

   ```sql
   SELECT * FROM task_reminders;
   SELECT * FROM past_reminders;
   ```

---

## Example Files

### **compose.yaml**

```yaml
services:
  vikunja:
    image: vikunja/vikunja
    environment:
      VIKUNJA_SERVICE_PUBLICURL: "http://<vikunja-domain>"
      VIKUNJA_DATABASE_HOST: "db"
      VIKUNJA_DATABASE_PASSWORD: "<your-database-password>"
      VIKUNJA_DATABASE_TYPE: "postgres"
      VIKUNJA_DATABASE_USER: "vikunja"
      VIKUNJA_DATABASE_DATABASE: "vikunja"
      VIKUNJA_SERVICE_JWTSECRET: "<your-jwt-secret>"
    ports:
      - 3456:3456
    volumes:
      - ./files:/app/vikunja/files
      - ./config:/etc/vikunja
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: "<your-database-password>"
      POSTGRES_USER: "vikunja"
    volumes:
      - ./db:/var/lib/postgresql/data
    healthcheck:
      test:
        - CMD-SHELL
        - pg_isready -h localhost -U $${POSTGRES_USER}
      interval: 2s
      timeout: 2s
      retries: 5
    restart: unless-stopped
    ports:
      - 5432:5432

  ntfy-handler:
    build:
      context: ./ntfy-handler
    container_name: ntfy-handler
    ports:
      - "4567:8000"
    volumes:
      - ./ntfy-handler/data:/app/data
    depends_on:
      - db
    environment:
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=vikunja
      - DB_USER=vikunja
      - DB_PASSWORD=<your-database-password>
```

---

### **config/config.yml**

```yaml
service:
  JWTSecret: "<your-jwt-secret>"
  publicurl: "http://<vikunja-domain>"

typesense:
  enabled: true
  url: "http://<typesense-domain>"
  apikey: "<your-typesense-api-key>"

cors:
  enabled: true
  origins:
   - "http://<auth-domain>"
```

# Recommended ways to generate secure secrets
# Using OpenSSL
```bash
openssl rand -base64 32
```
# Using Python

```python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Contributing

Contributions are welcome! If you encounter issues or have feature suggestions, feel free to open an issue or submit a pull request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details

---

## Acknowledgments

- [Vikunja](https://vikunja.io/) for its task management API
- [Ntfy](https://ntfy.sh/) for its lightweight notification system
- [Docker](https://www.docker.com/) for simplifying deployments

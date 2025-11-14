# Troubleshooting Guide

## Database Connection Issues

### Error: "password authentication failed for user 'postgres'" or "password authentication failed for user 'admin'"

This error occurs when there's a mismatch between the credentials in your `.env` file and what PostgreSQL expects.

#### Quick Fix

Run the automated fix script:

```powershell
.\fix-database.ps1
```

This will:
1. Check your current configuration
2. Stop and remove containers
3. Delete the database volume
4. Restart with correct credentials

#### Manual Fix

**Step 1: Check your .env file**

```powershell
notepad .env
```

Ensure these lines are present and have matching values:

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YourSecurePassword123
POSTGRES_DB=rightfax_testing
```

**Important**:
- Use the SAME password everywhere
- Don't use special characters that might need escaping
- Make sure there are no spaces around the `=` sign
- Make sure there are no trailing spaces

**Step 2: Completely reset the database**

```powershell
# Stop everything
docker compose down

# Remove ALL volumes (this deletes the database)
docker compose down -v

# Verify volumes are gone
docker volume ls | findstr rightfax
```

**Step 3: Start fresh**

```powershell
# Start services
docker compose up -d

# Wait for database to initialize (15-20 seconds)
Start-Sleep -Seconds 20

# Check PostgreSQL logs
docker compose logs postgres

# Check web logs
docker compose logs web
```

**Step 4: Verify connection**

```powershell
# Test database connection (replace 'postgres' with your POSTGRES_USER)
docker compose exec postgres psql -U postgres -d rightfax_testing -c "SELECT version();"
```

If this succeeds, the database is working correctly.

**Step 5: Test the web interface**

Navigate to http://localhost:8081/health

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Common Mistakes

1. **Mismatched credentials**: `.env` file has different password than what PostgreSQL initialized with
2. **Default values**: Not setting values in `.env`, so docker-compose uses defaults (admin/changeme)
3. **Typos**: `POSTGRES_USER` vs `POSTGRESQL_USER`
4. **Whitespace**: Spaces in the .env file like `POSTGRES_USER = postgres` (should be `POSTGRES_USER=postgres`)
5. **Not restarting**: Changing `.env` but not restarting containers

### Example Working .env File

```bash
# Database Configuration - USE THESE EXACT VALUES
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=rightfax_testing
POSTGRES_USER=postgres
POSTGRES_PASSWORD=MySecurePassword123

# RightFax Configuration
RIGHTFAX_API_URL=
RIGHTFAX_USERNAME=
RIGHTFAX_PASSWORD=
RIGHTFAX_FCL_DIRECTORY=./volumes/fcl
RIGHTFAX_XML_DIRECTORY=./volumes/xml

# Application Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
APP_PORT=5000
LOG_LEVEL=INFO

# Celery Configuration
REDIS_URL=redis://redis:6379/0

# Grafana Configuration
GRAFANA_PORT=3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin

# Nginx Configuration
NGINX_HTTP_PORT=8081
NGINX_HTTPS_PORT=443
```

### Verification Commands

```powershell
# Check what docker-compose sees
docker compose config | findstr POSTGRES

# Check running containers
docker compose ps

# Check if database is ready
docker compose exec postgres pg_isready -U postgres

# View web container environment
docker compose exec web env | findstr POSTGRES

# Check web container logs for connection errors
docker compose logs web | findstr -i "error\|password\|connection"
```

## Port Conflicts

### Error: "Ports are not available: port is already allocated"

**For port 8081:**

```powershell
# Find what's using port 8081
netstat -ano | findstr :8081

# If something is using it, either stop that service or change the port in .env:
# NGINX_HTTP_PORT=9000
```

**For port 5432 (PostgreSQL):**

```powershell
# Find what's using port 5432
netstat -ano | findstr :5432

# Change the port in .env:
# POSTGRES_PORT=5433

# Then update connection strings accordingly
```

## Container Won't Start

### Check logs

```powershell
# All containers
docker compose logs

# Specific container
docker compose logs web
docker compose logs postgres
docker compose logs celery_worker
```

### Rebuild containers

```powershell
# Stop and remove
docker compose down

# Rebuild
docker compose build --no-cache

# Start
docker compose up -d
```

## Web Interface Issues

### Blank page or 502 error

**Check if web container is running:**

```powershell
docker compose ps web
```

**Check web logs:**

```powershell
docker compose logs web --tail=50
```

**Restart web container:**

```powershell
docker compose restart web
```

### Can't access http://localhost:8081

**Check Nginx:**

```powershell
docker compose logs nginx
```

**Verify port mapping:**

```powershell
docker compose ps | findstr 8081
```

## Grafana Issues

### Can't log in to Grafana

Default credentials: `admin` / `admin`

If changed in `.env`, use the `GRAFANA_ADMIN_PASSWORD` value.

**Reset Grafana admin password:**

```powershell
docker compose exec grafana grafana-cli admin reset-admin-password newpassword
```

## File Permission Issues

### Can't write to volumes

**On Windows with Docker Desktop:**

1. Open Docker Desktop Settings
2. Go to Resources → File Sharing
3. Add your project directory
4. Apply & Restart

### Can't access FCL or XML directories

**Check if directories exist:**

```powershell
# From host
Test-Path .\volumes\fcl
Test-Path .\volumes\xml

# From container
docker compose exec web ls -la /mnt/rightfax/fcl
docker compose exec web ls -la /mnt/rightfax/xml
```

**Create directories if missing:**

```powershell
mkdir volumes\fcl
mkdir volumes\xml
```

## Complete Reset

If nothing else works, completely reset everything:

```powershell
# Stop all containers
docker compose down

# Remove all volumes (DELETES ALL DATA!)
docker compose down -v

# Remove all images
docker compose down --rmi all

# Clean Docker system
docker system prune -a --volumes

# Rebuild from scratch
docker compose build --no-cache
docker compose up -d
```

## Getting Help

If you're still having issues:

1. Run the diagnostic script: `.\check-config.ps1`
2. Check all logs: `docker compose logs > logs.txt`
3. Verify your `.env` file matches the example
4. Check Docker Desktop is running and has enough resources (4GB RAM minimum)

## Useful Diagnostic Commands

```powershell
# Show all environment variables in web container
docker compose exec web env

# Test database connection from web container
docker compose exec web python -c "from app.database import engine; print(engine.connect())"

# Show PostgreSQL version
docker compose exec postgres psql -U postgres -c "SELECT version();"

# Show all databases
docker compose exec postgres psql -U postgres -c "\l"

# Show all tables in rightfax_testing database
docker compose exec postgres psql -U postgres -d rightfax_testing -c "\dt"

# Check if tables were created
docker compose exec postgres psql -U postgres -d rightfax_testing -c "SELECT tablename FROM pg_tables WHERE schemaname='public';"
```

# RightFax Testing & Monitoring Platform

A Docker-containerized web application for load testing and performance monitoring of RightFax server infrastructure.

## Features

- **Flexible Fax Submission**: Submit configurable batches of test faxes via FCL or REST API
- **Real-time Monitoring**: Track fax transmission metrics with Grafana dashboards
- **XML Processing**: Automatically parse and store RightFax completion files
- **Performance Analytics**: Analyze throughput, success rates, and call durations
- **Web Interface**: User-friendly dashboard for managing test batches

## Architecture

The platform consists of the following containerized services:

- **Web Application** (Flask): User interface and API
- **PostgreSQL**: Data storage for submissions and completions
- **Redis**: Message broker for Celery tasks
- **Celery Worker**: Background task processing
- **XML Watcher**: Monitors and processes RightFax XML files
- **Grafana**: Performance monitoring dashboards
- **Nginx**: Reverse proxy

## Prerequisites

- Docker and Docker Compose installed
- Access to RightFax server infrastructure
- Mounted directories for FCL submission and XML output

> **Windows Users**: See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed Windows-specific instructions including Docker Desktop setup, PowerShell scripts, and troubleshooting.

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd otfdashboard2
```

### 2. Configure Environment

Copy the example environment file and edit with your settings:

```bash
cp .env.example .env
```

Edit `.env` and configure:

```bash
# Database credentials
POSTGRES_PASSWORD=your_secure_password

# RightFax configuration
RIGHTFAX_API_URL=https://your-rightfax-server/api/v2
RIGHTFAX_USERNAME=your_rightfax_username
RIGHTFAX_PASSWORD=your_rightfax_password
RIGHTFAX_FCL_DIRECTORY=/path/to/rightfax/fcl
RIGHTFAX_XML_DIRECTORY=/path/to/rightfax/xml

# Grafana credentials
GRAFANA_ADMIN_PASSWORD=your_grafana_password
```

### 3. Start the Platform

```bash
docker compose up -d
```

### 4. Access the Application

- **Web Interface**: http://localhost
- **Grafana Dashboard**: http://localhost:3000 (admin/admin or configured password)
- **API**: http://localhost/api

## Quick Start for Windows (Docker Desktop)

### Prerequisites

1. **Install Docker Desktop for Windows**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Ensure WSL 2 backend is enabled (recommended)
   - Minimum requirements: Windows 10 64-bit (Pro, Enterprise, or Education)
   - Enable Hyper-V and Containers Windows features if prompted

2. **Verify Docker Installation**
   - Open PowerShell or Command Prompt
   - Run: `docker --version`
   - Run: `docker compose version`

### Step-by-Step Setup

#### 1. Clone or Download the Repository

**Option A: Using Git**
```powershell
# Open PowerShell
cd C:\Users\YourUsername\Documents
git clone <repository-url>
cd otfdashboard2
```

**Option B: Download ZIP**
- Download the repository as ZIP
- Extract to a location like `C:\Users\YourUsername\Documents\otfdashboard2`
- Open PowerShell and navigate to the folder:
  ```powershell
  cd C:\Users\YourUsername\Documents\otfdashboard2
  ```

#### 2. Configure Environment Variables

Create your `.env` file from the example:

```powershell
# Copy the example file
Copy-Item .env.example .env

# Edit with Notepad
notepad .env
```

**Important Configuration for Windows:**

```bash
# Database Configuration
POSTGRES_PASSWORD=YourSecurePassword123

# RightFax Configuration
RIGHTFAX_API_URL=https://your-rightfax-server/api/v2
RIGHTFAX_USERNAME=your_username
RIGHTFAX_PASSWORD=your_password

# IMPORTANT: Use forward slashes (/) even on Windows
# Option 1: Use local volumes (recommended for testing)
RIGHTFAX_FCL_DIRECTORY=./volumes/fcl
RIGHTFAX_XML_DIRECTORY=./volumes/xml

# Option 2: Use network path to RightFax server
# RIGHTFAX_FCL_DIRECTORY=//server/share/rightfax/fcl
# RIGHTFAX_XML_DIRECTORY=//server/share/rightfax/xml

# Option 3: Use Windows path (will be converted inside container)
# RIGHTFAX_FCL_DIRECTORY=C:/RightFax/FCL
# RIGHTFAX_XML_DIRECTORY=C:/RightFax/XML

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=YourGrafanaPassword123
```

**Path Configuration Notes:**
- Always use **forward slashes** (`/`) in paths, not backslashes (`\`)
- For local testing, use `./volumes/fcl` and `./volumes/xml` (these will be created automatically)
- For production, map to your actual RightFax server directories
- UNC paths work: `//server/share/path`
- Windows paths work but use forward slashes: `C:/RightFax/FCL`

#### 3. Configure Docker Desktop Settings

1. **Open Docker Desktop** from Start Menu
2. **Go to Settings** (gear icon)
3. **Resources → File Sharing**
   - Add the folder where you cloned the project (e.g., `C:\Users\YourUsername\Documents\otfdashboard2`)
   - If using RightFax directories on C: drive, add those paths too
4. **Resources → WSL Integration** (if using WSL 2)
   - Enable integration with your WSL distribution
5. **Apply & Restart** Docker Desktop

#### 4. Start the Platform

Open PowerShell in the project directory and run:

```powershell
# Start all services
docker compose up -d

# Wait 10-15 seconds for services to initialize

# Check that all services are running
docker compose ps
```

You should see 6 services running:
- rightfax_web
- rightfax_postgres
- rightfax_redis
- rightfax_celery_worker
- rightfax_xml_watcher
- rightfax_grafana
- rightfax_nginx

#### 5. Access the Application

Open your web browser:
- **Main Dashboard**: http://localhost
- **Grafana**: http://localhost:3000 (login: admin/admin)
- **API Health Check**: http://localhost/health

#### 6. View Logs (Optional)

To see what's happening:

```powershell
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f web
docker compose logs -f celery_worker
docker compose logs -f xml_watcher

# Press Ctrl+C to stop viewing logs
```

### Windows-Specific Troubleshooting

#### Issue: "Cannot connect to Docker daemon"
**Solution**: Ensure Docker Desktop is running
- Start Docker Desktop from the Start Menu
- Wait for the green "Docker is running" indicator

#### Issue: "Error response from daemon: Ports are not available"
**Solution**: Port 80 or other ports already in use
```powershell
# Find what's using port 80
netstat -ano | findstr :80

# Change ports in .env file if needed
echo "NGINX_HTTP_PORT=8080" >> .env

# Then use: http://localhost:8080
```

#### Issue: "Drive has not been shared"
**Solution**:
1. Open Docker Desktop Settings
2. Resources → File Sharing
3. Add your project directory
4. Apply & Restart

#### Issue: Line Ending Problems
**Solution**: Git may convert line endings on Windows
```powershell
# If start.sh has issues, convert line endings
dos2unix start.sh  # Or use Notepad++ to convert to Unix (LF)
```

#### Issue: Permission Denied on Volumes
**Solution**:
1. Ensure Docker Desktop has permissions to access the folders
2. Run PowerShell as Administrator if needed
3. Check Windows Defender or antivirus isn't blocking Docker

#### Issue: Slow Performance
**Solution**:
1. Docker Desktop Settings → Resources
2. Increase Memory to at least 4 GB
3. Increase CPUs to at least 2
4. Apply & Restart

### Stopping the Platform

```powershell
# Stop all services (keeps data)
docker compose down

# Stop and remove all data (CAUTION: Deletes database!)
docker compose down -v
```

### Restarting the Platform

```powershell
# Start again
docker compose up -d

# Or restart specific service
docker compose restart web
```

### Connecting to RightFax Server

If RightFax is on a different Windows server:

1. **Network Share Method** (Recommended):
   ```bash
   # In .env file
   RIGHTFAX_FCL_DIRECTORY=//rightfax-server/RightFax/FCL
   RIGHTFAX_XML_DIRECTORY=//rightfax-server/RightFax/XML
   ```

2. **Mapped Drive Method**:
   - Map the RightFax directories as network drives (e.g., R:\FCL)
   - Use forward slashes in .env: `RIGHTFAX_FCL_DIRECTORY=R:/FCL`

3. **Docker Desktop File Sharing**:
   - Add the network paths in Docker Desktop → Settings → Resources → File Sharing
   - Restart Docker Desktop

### Getting Help

If you encounter issues:

1. Check the logs: `docker compose logs`
2. Verify .env configuration: `notepad .env`
3. Restart Docker Desktop
4. Check Docker Desktop troubleshooting: https://docs.docker.com/desktop/troubleshoot/overview/

## Usage

### Submitting a Test Batch

1. Navigate to http://localhost/submit
2. Configure batch parameters:
   - **Batch Name**: Descriptive name for the test
   - **Number of Faxes**: How many faxes to send (1-100,000)
   - **Timing**: Immediate or interval-based (1-300 seconds between faxes)
   - **Recipient Phone**: Fax number to send to
   - **Account**: RightFax account to use
   - **Method**: FCL (file drop) or REST API
3. Click "Submit Batch"

### Monitoring Performance

1. Access Grafana at http://localhost:3000
2. Navigate to "RightFax Performance Monitoring" dashboard
3. View metrics:
   - Jobs per minute
   - Success rate
   - Call duration percentiles
   - Concurrent calls
   - Error distribution

### Managing Batches

- View all batches at http://localhost/batches
- Monitor active batch progress in real-time
- Delete completed batches
- Reset database (delete all data) if needed

## API Endpoints

### Batches

- `GET /api/batches` - List all batches
- `POST /api/batches` - Create new batch
- `GET /api/batches/:id` - Get batch details
- `DELETE /api/batches/:id` - Delete batch

### Statistics

- `GET /api/stats` - Overall statistics
- `GET /api/completions` - List fax completions

### Utilities

- `GET /health` - Health check
- `POST /api/database/reset` - Delete all data (requires confirmation)

## Directory Structure

```
otfdashboard2/
├── app/                    # Flask application
│   ├── models.py          # Database models
│   ├── routes/            # API and web routes
│   ├── services/          # Business logic
│   │   ├── fcl_generator.py    # FCL file generation
│   │   ├── rightfax_api.py     # RightFax API client
│   │   ├── xml_parser.py       # XML parsing
│   │   └── xml_watcher.py      # File monitoring
│   ├── tasks/             # Celery tasks
│   └── templates/         # HTML templates
├── database/              # Database initialization
├── grafana/              # Grafana configuration
├── nginx/                # Nginx configuration
├── docker-compose.yml    # Container orchestration
├── Dockerfile           # Application container
└── requirements.txt     # Python dependencies
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_PASSWORD` | PostgreSQL password | changeme |
| `POSTGRES_DB` | Database name | rightfax_testing |
| `RIGHTFAX_API_URL` | RightFax REST API endpoint | - |
| `RIGHTFAX_USERNAME` | RightFax API username | - |
| `RIGHTFAX_PASSWORD` | RightFax API password | - |
| `RIGHTFAX_FCL_DIRECTORY` | FCL file drop location | /mnt/rightfax/fcl |
| `RIGHTFAX_XML_DIRECTORY` | XML output directory | /mnt/rightfax/xml |
| `LOG_LEVEL` | Logging level | INFO |

### Volume Mounts

The platform requires the following directories:

- **FCL Directory**: Where RightFax monitors for incoming fax submission files
- **XML Directory**: Where RightFax writes fax completion XML files

Configure these paths in `.env` or mount them in `docker-compose.yml`.

## FCL File Format

The platform generates FCL (Fax Command Language) files in the following format:

```
{{begin}}

{{fax 555-1234}}
{{attach C:\\Path\\To\\Document.pdf}}

{{winsecid ACCOUNT_NAME}}

{{end}}
```

See the [Integration Module Administrator Guide](docs/) for complete FCL specifications.

## XML Processing

The platform automatically processes RightFax XML completion files with the following workflow:

1. **Detection**: File watcher detects new `.xml` files
2. **Parsing**: Extracts job metadata (duration, status, pages, etc.)
3. **Storage**: Saves to PostgreSQL database
4. **Archiving**: Moves processed files to archive directory
5. **Cleanup**: Removes archives older than retention period (90 days)

## Troubleshooting

### Services Not Starting

```bash
# Check container logs
docker compose logs web
docker compose logs postgres

# Verify environment configuration
cat .env
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker compose ps postgres

# Test database connection
docker compose exec postgres psql -U admin -d rightfax_testing
```

### FCL Files Not Processing

- Verify `RIGHTFAX_FCL_DIRECTORY` is correctly mounted
- Check directory permissions (must be writable)
- Review logs: `docker compose logs celery_worker`

### XML Files Not Processing

- Verify `RIGHTFAX_XML_DIRECTORY` is correctly mounted
- Check XML watcher logs: `docker compose logs xml_watcher`
- Ensure XML files match expected schema

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=app.main:app
export FLASK_ENV=development

# Run Flask application
flask run
```

### Running Tests

```bash
pytest
```

## Database Schema

The platform uses the following main tables:

- **submission_batches**: Batch submission records
- **fax_submissions**: Individual fax submission records
- **fax_completions**: Parsed completion data from XML
- **rightfax_accounts**: Available RightFax accounts
- **system_config**: Application configuration

See [database/init.sql](database/init.sql) for complete schema.

## Maintenance

### Backup Database

```bash
docker compose exec postgres pg_dump -U admin rightfax_testing > backup.sql
```

### Restore Database

```bash
cat backup.sql | docker compose exec -T postgres psql -U admin rightfax_testing
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f celery_worker
docker compose logs -f xml_watcher
```

### Stop Platform

```bash
docker compose down
```

### Reset Everything (including data)

```bash
docker compose down -v
```

## Security Considerations

- Change default passwords in `.env`
- Enable HTTPS in production (configure Nginx SSL)
- Restrict database access
- Validate file uploads
- Implement authentication for web interface (currently basic auth)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:

- Review documentation in `/docs` directory
- Check container logs
- Verify configuration in `.env`

## Version

Current Version: 1.0.0

## Acknowledgments

Built for RightFax infrastructure testing and monitoring.

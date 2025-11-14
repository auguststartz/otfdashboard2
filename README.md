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
RIGHTFAX_API_KEY=your_api_key
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
| `RIGHTFAX_API_KEY` | API authentication key | - |
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

# Windows Setup Guide for RightFax Testing & Monitoring Platform

Complete guide for setting up and running the platform on Windows with Docker Desktop.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installing Docker Desktop](#installing-docker-desktop)
3. [First-Time Setup](#first-time-setup)
4. [Configuration](#configuration)
5. [Starting the Platform](#starting-the-platform)
6. [Common Issues](#common-issues)
7. [RightFax Integration](#rightfax-integration)
8. [Best Practices](#best-practices)

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 64-bit (version 2004 or higher) or Windows 11
- **Edition**: Pro, Enterprise, or Education (Home edition requires WSL 2)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk**: 20 GB free space
- **CPU**: 64-bit processor with Second Level Address Translation (SLAT)

### Required Windows Features
- Hyper-V and Containers (enabled automatically by Docker Desktop)
- Windows Subsystem for Linux (WSL 2) - recommended backend
- Virtualization enabled in BIOS

## Installing Docker Desktop

### Step 1: Download Docker Desktop

1. Visit: https://www.docker.com/products/docker-desktop/
2. Click "Download for Windows"
3. Run the installer: `Docker Desktop Installer.exe`

### Step 2: Installation Options

During installation, ensure:
- ✅ **Use WSL 2 instead of Hyper-V** (recommended)
- ✅ **Add shortcut to desktop**

### Step 3: Initial Configuration

After installation:

1. **Start Docker Desktop** from Start Menu
2. **Accept the Service Agreement**
3. **Skip the tutorial** (or complete it for familiarity)
4. Wait for "Docker Desktop is running" message

### Step 4: Verify Installation

Open PowerShell and run:

```powershell
docker --version
docker compose version
```

Expected output:
```
Docker version 24.x.x, build xxxxxxx
Docker Compose version v2.x.x
```

## First-Time Setup

### Option 1: Quick Start (Using Scripts)

1. **Download or clone the repository**
2. **Open PowerShell as Administrator** (right-click, "Run as Administrator")
3. **Navigate to the project folder**:
   ```powershell
   cd C:\Users\YourUsername\Documents\otfdashboard2
   ```
4. **Run the startup script**:
   ```powershell
   .\start.ps1
   ```
   Or double-click `start.bat` in File Explorer

The script will:
- Check Docker installation
- Create .env file if needed
- Create necessary directories
- Start all services
- Open the application in your browser

### Option 2: Manual Setup

#### 1. Download the Project

**Using Git:**
```powershell
cd C:\Users\YourUsername\Documents
git clone https://github.com/yourusername/otfdashboard2.git
cd otfdashboard2
```

**Or download ZIP:**
- Download and extract to `C:\Users\YourUsername\Documents\otfdashboard2`

#### 2. Configure Docker Desktop File Sharing

1. Open Docker Desktop
2. Click Settings (gear icon)
3. Go to **Resources → File Sharing**
4. Add your project directory:
   - `C:\Users\YourUsername\Documents\otfdashboard2`
5. Click **Apply & Restart**

#### 3. Create Configuration File

```powershell
# Copy the example
Copy-Item .env.example .env

# Edit with Notepad
notepad .env
```

#### 4. Start Services

```powershell
docker compose up -d
```

## Configuration

### Basic Configuration (.env file)

Create your `.env` file from the template:

```powershell
Copy-Item .env.example .env
notepad .env
```

### Required Settings

```bash
# Database
POSTGRES_PASSWORD=YourSecurePassword123

# RightFax API
RIGHTFAX_API_URL=https://rightfax-server.yourdomain.com/api/v2
RIGHTFAX_USERNAME=your_username
RIGHTFAX_PASSWORD=your_password

# Grafana
GRAFANA_ADMIN_PASSWORD=YourGrafanaPassword123
```

### Path Configuration Options

#### Option 1: Local Testing (Default)
```bash
RIGHTFAX_FCL_DIRECTORY=./volumes/fcl
RIGHTFAX_XML_DIRECTORY=./volumes/xml
```
Files are stored locally in the project folder.

#### Option 2: Network Share (Recommended for Production)
```bash
RIGHTFAX_FCL_DIRECTORY=//rightfax-server/RightFax/FCL
RIGHTFAX_XML_DIRECTORY=//rightfax-server/RightFax/XML
```
Connects directly to RightFax server's shared directories.

#### Option 3: Mapped Network Drive
```bash
# First, map drives in Windows:
# R: → \\rightfax-server\RightFax\FCL
# X: → \\rightfax-server\RightFax\XML

RIGHTFAX_FCL_DIRECTORY=R:/
RIGHTFAX_XML_DIRECTORY=X:/
```

#### Option 4: Local Windows Path
```bash
# If RightFax is on the same machine
RIGHTFAX_FCL_DIRECTORY=C:/RightFax/FCL
RIGHTFAX_XML_DIRECTORY=C:/RightFax/XML
```

**Important Path Rules:**
- ✅ Always use forward slashes: `/`
- ✅ UNC paths: `//server/share/path`
- ✅ Drive letters: `C:/folder/path`
- ❌ Never use backslashes: `\`

## Starting the Platform

### Using PowerShell Script (Recommended)

```powershell
# Right-click start.bat and "Run as Administrator"
# Or in PowerShell:
.\start.ps1
```

### Using Docker Compose

```powershell
# Start all services
docker compose up -d

# View status
docker compose ps

# View logs
docker compose logs -f
```

### Accessing the Application

Open your browser:
- **Dashboard**: http://localhost
- **Grafana**: http://localhost:3000 (login: admin/admin)
- **API**: http://localhost/api
- **Health**: http://localhost/health

### First Login

1. Navigate to http://localhost
2. You should see the RightFax Testing Platform dashboard
3. Click "Submit Batch" to create your first test
4. Open http://localhost:3000 for Grafana monitoring

## Common Issues

### Issue: "Docker daemon is not running"

**Symptoms**: `Error: Cannot connect to the Docker daemon`

**Solution**:
1. Open Docker Desktop from Start Menu
2. Wait 30-60 seconds for Docker to fully start
3. Look for "Docker Desktop is running" in the system tray
4. Try the command again

### Issue: Port 80 Already in Use

**Symptoms**: `Error: Ports are not available: port is already allocated`

**Solution 1**: Stop IIS or other services using port 80
```powershell
# Check what's using port 80
netstat -ano | findstr :80

# Stop IIS (if applicable)
iisreset /stop
```

**Solution 2**: Change the port in .env
```bash
# In .env file
NGINX_HTTP_PORT=8080
```
Then access at: http://localhost:8080

### Issue: Drive Not Shared

**Symptoms**: `Error: Mounts denied` or `drive has not been shared`

**Solution**:
1. Open Docker Desktop Settings
2. Go to **Resources → File Sharing**
3. Add the following paths:
   - Your project directory
   - Any RightFax directories you're accessing
4. Click **Apply & Restart**

### Issue: Network Path Not Accessible

**Symptoms**: Can't access `//server/share` paths

**Solution**:
1. **Test the path in File Explorer first**:
   - Open File Explorer
   - Type `\\server\share` in the address bar
   - Enter credentials if prompted
2. **Add network credentials to Windows**:
   ```powershell
   # Store credentials
   cmdkey /add:server /user:domain\username /pass:password
   ```
3. **Configure Docker Desktop**:
   - Settings → Resources → File Sharing
   - Add `\\server\share`
   - Apply & Restart

### Issue: Permission Denied

**Symptoms**: `Permission denied` errors on volumes

**Solution**:
1. Run PowerShell as Administrator
2. Check antivirus isn't blocking Docker
3. Ensure Docker has proper permissions:
   - Docker Desktop Settings → General
   - Enable "Expose daemon on tcp://localhost:2375 without TLS" (for troubleshooting only)

### Issue: Containers Keep Restarting

**Symptoms**: Services show status "Restarting" in `docker compose ps`

**Solution**:
```powershell
# Check logs for errors
docker compose logs web
docker compose logs postgres

# Common fixes:
# 1. Invalid .env configuration
notepad .env

# 2. Port conflicts
docker compose down
netstat -ano | findstr "80 3000 5000 5432 6379"

# 3. Insufficient resources
# Docker Desktop → Settings → Resources
# Increase Memory to 4 GB and CPUs to 2
```

### Issue: Slow Performance

**Symptoms**: Very slow startup or operation

**Solution**:
1. Increase Docker resources:
   - Open Docker Desktop Settings
   - Go to **Resources**
   - Set **Memory** to 4 GB minimum (8 GB recommended)
   - Set **CPUs** to 2 minimum (4 recommended)
   - Click **Apply & Restart**

2. Check WSL 2 is being used:
   - Docker Desktop → Settings → General
   - Ensure "Use the WSL 2 based engine" is checked

3. Disable antivirus real-time scanning for Docker directories

## RightFax Integration

### Scenario 1: RightFax on Same Windows Machine

If RightFax is installed on your local machine:

```bash
# In .env
RIGHTFAX_API_URL=http://localhost:8080/api
RIGHTFAX_FCL_DIRECTORY=C:/Program Files/RightFax/FCL
RIGHTFAX_XML_DIRECTORY=C:/Program Files/RightFax/XML
```

**Docker Desktop File Sharing**:
- Add `C:\Program Files\RightFax` to File Sharing

### Scenario 2: RightFax on Different Server

#### Using Network Shares (Recommended)

```bash
# In .env
RIGHTFAX_API_URL=https://rightfax-server.domain.com/api/v2
RIGHTFAX_FCL_DIRECTORY=//rightfax-server/RightFax$/FCL
RIGHTFAX_XML_DIRECTORY=//rightfax-server/RightFax$/XML
```

**Configure Credentials**:
```powershell
# Save network credentials
cmdkey /add:rightfax-server /user:DOMAIN\username /pass:password
```

**Docker Desktop File Sharing**:
- Add `\\rightfax-server\RightFax$` to File Sharing

#### Using Mapped Drives

1. **Map network drives in Windows**:
   ```powershell
   # In PowerShell
   New-PSDrive -Name "R" -PSProvider FileSystem -Root "\\rightfax-server\RightFax$\FCL" -Persist
   New-PSDrive -Name "X" -PSProvider FileSystem -Root "\\rightfax-server\RightFax$\XML" -Persist
   ```

2. **Update .env**:
   ```bash
   RIGHTFAX_FCL_DIRECTORY=R:/
   RIGHTFAX_XML_DIRECTORY=X:/
   ```

3. **Docker Desktop File Sharing**:
   - Add `R:\` and `X:\` drives

### Testing RightFax Connection

```powershell
# Test API connection
curl http://localhost/health

# Test FCL directory access
docker compose exec web ls /mnt/rightfax/fcl

# Test XML directory access
docker compose exec web ls /mnt/rightfax/xml

# Check container logs
docker compose logs web
```

## Best Practices

### 1. Use WSL 2 Backend

WSL 2 provides better performance than Hyper-V:
- Docker Desktop → Settings → General
- Enable "Use the WSL 2 based engine"

### 2. Allocate Sufficient Resources

Recommended Docker Desktop resources:
- **Memory**: 4-8 GB
- **CPUs**: 2-4 cores
- **Disk**: 20 GB+

### 3. Regular Updates

Keep Docker Desktop updated:
- Check for updates in Docker Desktop
- Update monthly or when prompted

### 4. Monitor Disk Usage

Docker can consume significant disk space:
```powershell
# Check Docker disk usage
docker system df

# Clean up (removes stopped containers, unused networks, dangling images)
docker system prune

# Clean everything (CAUTION: removes volumes too)
docker system prune -a --volumes
```

### 5. Backup Configuration

Backup your `.env` file regularly:
```powershell
Copy-Item .env .env.backup
```

### 6. Use Local Volumes for Testing

For initial testing, use local volumes:
```bash
RIGHTFAX_FCL_DIRECTORY=./volumes/fcl
RIGHTFAX_XML_DIRECTORY=./volumes/xml
```

Switch to network paths after confirming the platform works.

### 7. Secure Passwords

Use strong passwords in `.env`:
```bash
POSTGRES_PASSWORD=$(openssl rand -base64 32)
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 32)
```

Or use a password manager to generate strong passwords.

## Maintenance

### Viewing Logs

```powershell
# All services
docker compose logs -f

# Specific service
docker compose logs -f web
docker compose logs -f xml_watcher

# Last 100 lines
docker compose logs --tail=100
```

### Restarting Services

```powershell
# Restart all
docker compose restart

# Restart specific service
docker compose restart web

# Restart with rebuild
docker compose up -d --force-recreate
```

### Updating the Platform

```powershell
# Stop services
docker compose down

# Pull latest changes (if using Git)
git pull

# Rebuild and start
docker compose up -d --build
```

### Database Backup

```powershell
# Backup database
docker compose exec postgres pg_dump -U admin rightfax_testing > backup.sql

# Restore database
Get-Content backup.sql | docker compose exec -T postgres psql -U admin rightfax_testing
```

## Getting Help

If you encounter issues not covered here:

1. **Check logs**: `docker compose logs`
2. **Verify configuration**: `notepad .env`
3. **Test Docker**: `docker ps`
4. **Restart Docker Desktop**
5. **Check Docker Desktop troubleshooting**: https://docs.docker.com/desktop/troubleshoot/overview/
6. **Review README.md** for general documentation

## Quick Reference

### Essential Commands

```powershell
# Start platform
docker compose up -d

# Stop platform
docker compose down

# View status
docker compose ps

# View logs
docker compose logs -f

# Restart service
docker compose restart web

# Rebuild and start
docker compose up -d --build

# Stop and remove everything
docker compose down -v
```

### Default URLs

- Dashboard: http://localhost
- Grafana: http://localhost:3000
- API: http://localhost/api
- Health: http://localhost/health

### Default Credentials

- Grafana: admin/admin (change on first login)
- Database: admin/changeme (set in .env)

## Summary

You should now have the RightFax Testing & Monitoring Platform running on Windows with Docker Desktop. For daily use:

1. Start Docker Desktop
2. Run `docker compose up -d` or use `start.ps1`
3. Access http://localhost in your browser
4. Submit test batches and monitor in Grafana

For questions or issues, refer to the main README.md or check the logs with `docker compose logs`.

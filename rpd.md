# Product Requirements Document: RightFax Testing & Monitoring Platform

**Version:** 1.1
**Date:** November 14, 2025
**Author:** August Startz
**Status:** Draft

---

## Executive Summary

The RightFax Testing & Monitoring Platform is a Docker-containerized web application designed to streamline load testing and performance monitoring of RightFax server infrastructure. The solution addresses the need for controlled fax submission testing and real-time performance analytics through two integrated components: a flexible fax submission tool and an automated monitoring dashboard.

This platform will enable technical teams to simulate various load scenarios, measure system performance under different conditions, and gain actionable insights into fax server capacity and behavior.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Goals and Objectives](#goals-and-objectives)
3. [Target Users](#target-users)
4. [User Stories](#user-stories)
5. [Functional Requirements](#functional-requirements)
6. [Technical Requirements](#technical-requirements)
7. [System Architecture](#system-architecture)
8. [Data Models](#data-models)
9. [User Interface Requirements](#user-interface-requirements)
10. [Integration Specifications](#integration-specifications)
11. [Success Metrics](#success-metrics)
12. [Implementation Phases](#implementation-phases)
13. [Risks and Mitigations](#risks-and-mitigations)
14. [Future Enhancements](#future-enhancements)

---

## Problem Statement

Healthcare organizations and enterprises relying on RightFax infrastructure lack efficient tools to:

- **Conduct controlled load testing** of fax servers to determine capacity limits
- **Simulate realistic usage patterns** with configurable timing and volume
- **Monitor performance metrics** in real-time during testing scenarios
- **Analyze historical performance data** to inform infrastructure decisions
- **Validate system behavior** before production deployments or upgrades

Current manual testing approaches are time-consuming, inconsistent, and lack comprehensive metrics collection, making it difficult to optimize fax infrastructure or troubleshoot performance issues.

---

## Goals and Objectives

### Primary Goals

1. **Enable Flexible Load Testing**: Provide a user-friendly interface for submitting configurable batches of test faxes to RightFax servers
2. **Automate Performance Monitoring**: Capture and visualize real-time fax transmission metrics without manual intervention
3. **Support Multiple Integration Methods**: Implement both FCL file-based and REST API submission methods for maximum compatibility
4. **Deliver Actionable Insights**: Present performance data through intuitive Grafana dashboards for quick analysis

### Success Criteria

- Submit batches of 1-100000+ faxes with configurable timing intervals
- Support both FCL and REST API submission methods
- Parse and store 100% of RightFax XML completion files
- Display metrics in Grafana with <5 second data lag
- Process and visualize historical data for trend analysis
- Containerized deployment with simple configuration

---

## Target Users

### Primary Users
- **Solutions Consultants**: Testing system capacity for customer implementations
- **System Administrators**: Monitoring and optimizing RightFax server performance
- **Technical Support Engineers**: Troubleshooting performance issues and bottlenecks

### Secondary Users
- **IT Management**: Reviewing performance trends and capacity planning
- **QA Teams**: Validating system behavior during testing cycles

---

## User Stories

### Fax Submission Tool

**As a Solutions Consultant, I want to:**
- Configure a batch of test faxes with specific parameters so I can simulate customer usage patterns
- Choose between sending faxes immediately or with timed intervals so I can test different load scenarios
- Select submission method (FCL or REST API) so I can test both integration approaches
- Monitor submission progress in real-time so I know when tests are complete

**As a System Administrator, I want to:**
- Submit controlled loads to specific fax accounts so I can test account-level configurations
- Vary the timing between submissions so I can observe system behavior under different conditions
- Use realistic cover pages and attachments so testing reflects production usage

### Monitoring Dashboard

**As a Technical Support Engineer, I want to:**
- View real-time metrics of fax completions so I can monitor active tests
- See historical trends of jobs per minute so I can identify capacity patterns
- Analyze call duration statistics so I can spot performance anomalies
- Identify peak concurrent call loads so I can understand system limits

**As an IT Manager, I want to:**
- Review aggregated performance metrics so I can make infrastructure decisions
- Compare performance across different time periods so I can track improvements
- Export metrics data so I can include it in reports

---

## Functional Requirements

### 5.1 Fax Submission Tool

#### 5.1.1 Batch Configuration
**REQ-SUBMIT-001**: The system SHALL allow users to specify the number of faxes to submit in a batch (range: 1-100,000)

**REQ-SUBMIT-002**: The system SHALL provide two timing options:
- Immediate: Submit all faxes as quickly as possible
- Interval-based: Submit faxes with configurable delay (range: 1-300 seconds between submissions)

**REQ-SUBMIT-003**: The system SHALL validate that interval timing multiplied by batch size does not exceed reasonable test durations (e.g., warn if total time >24 hours)

#### 5.1.2 Fax Parameters
**REQ-SUBMIT-004**: The system SHALL allow users to specify per batch:
- Recipient phone number (no format validation required)
- Cover page recipient name
- RightFax account to send from (and password to use for that account)
- Attachment file (PDF, TIFF, or supported formats)

**REQ-SUBMIT-005**: The system SHALL support attachment upload with:
- Maximum file size: 25 MB
- Supported formats: PDF, TIFF, DOC, DOCX
- File validation before submission

**REQ-SUBMIT-006**: The system SHALL allow users to optionally randomize recipient names across a batch for more realistic testing

#### 5.1.3 Submission Methods
**REQ-SUBMIT-007**: The system SHALL support FCL (Fax Command Language) submission by:
- Generating properly formatted FCL text files
- Writing files to configurable directory monitored by RightFax
- Including all required FCL parameters (see Integration Specifications)
- Generating unique filenames to prevent conflicts

**REQ-SUBMIT-008**: The system SHALL support REST API submission by:
- Authenticating to RightFax REST API
- Formatting requests per API specification
- Handling API responses and errors
- Retrying failed submissions with exponential backoff

**REQ-SUBMIT-009**: The system SHALL allow users to select submission method (FCL or REST API) per batch

#### 5.1.4 Progress Tracking
**REQ-SUBMIT-010**: The system SHALL display real-time submission progress including:
- Number of faxes submitted
- Number remaining
- Current submission rate
- Estimated completion time

**REQ-SUBMIT-011**: The system SHALL log all submissions with:
- Timestamp
- Submission method
- Parameters used
- Success/failure status
- Job IDs returned by RightFax

**REQ-SUBMIT-012**: The system SHALL allow users to cancel in-progress batch submissions

#### 5.1.5 Historical Tracking
**REQ-SUBMIT-013**: The system SHALL maintain a history of previous batch submissions accessible through the UI

**REQ-SUBMIT-014**: The system SHALL allow users to duplicate previous batch configurations for repeated testing

### 5.2 XML Parsing and Data Collection

#### 5.2.1 File Monitoring
**REQ-PARSE-001**: The system SHALL monitor a configurable directory for new XML files written by RightFax

**REQ-PARSE-002**: The system SHALL detect new XML files within 5 seconds of file creation

**REQ-PARSE-003**: The system SHALL handle multiple XML files arriving simultaneously without data loss

#### 5.2.2 XML Processing
**REQ-PARSE-004**: The system SHALL parse RightFax XML completion files and extract:
- Job ID
- Submission timestamp
- Completion timestamp
- Duration
- Success/failure status
- Error codes (if applicable)
- Recipient phone number
- Pages transmitted
- Account used
- Call attempt count
- Any additional metadata available

**REQ-PARSE-005**: The system SHALL validate XML structure before parsing and log malformed files

**REQ-PARSE-006**: The system SHALL move processed XML files to an archive directory with timestamp

**REQ-PARSE-007**: The system SHALL handle parsing errors gracefully without stopping the monitoring process

#### 5.2.3 Database Storage
**REQ-PARSE-008**: The system SHALL store parsed data in PostgreSQL database with appropriate indexing for time-series queries

**REQ-PARSE-009**: The system SHALL normalize data types for consistent querying

**REQ-PARSE-010**: The system SHALL handle duplicate XML files by detecting and skipping based on job ID

**REQ-PARSE-011**: The system SHALL maintain referential integrity between submission logs and completion data when possible

**REQ-PARSE-011**: The system SHALL allow the user to delete all data from the database to wipe the slate clean

### 5.3 Grafana Dashboard

#### 5.3.1 Core Metrics
**REQ-DASH-001**: The system SHALL provide Grafana dashboard panels displaying:
- **Jobs per minute** (real-time and historical)
- **Maximum concurrent calls** at any given time
- **Average call duration** with percentile breakdowns (p50, p90, p99)
- **Success rate** (percentage and count)
- **Error distribution** by error code
- **Call attempts histogram** (first attempt success vs. retries)

#### 5.3.2 Time Range Analysis
**REQ-DASH-002**: The system SHALL support time range selection (last 5 min, 15 min, 1 hour, 6 hours, 24 hours, 7 days, 30 days, custom)

**REQ-DASH-003**: The system SHALL automatically refresh dashboards with configurable intervals (default: 5 seconds)

#### 5.3.3 Filtering and Drill-down
**REQ-DASH-004**: The system SHALL allow filtering by:
- Account
- Success/failure status
- Phone number pattern
- Date range

**REQ-DASH-005**: The system SHALL provide drill-down capability from aggregate metrics to individual job details

#### 5.3.4 Alerting
**REQ-DASH-006**: The system SHOULD support Grafana alerting for:
- Error rate exceeding threshold
- Average duration exceeding threshold
- System processing lag exceeding threshold

---

## Technical Requirements

### 6.1 Technology Stack

#### Core Technologies
- **Backend Framework**: Python 3.11+ (Flask or FastAPI)
- **Database**: PostgreSQL 15+
- **Monitoring**: Grafana 10+
- **Containerization**: Docker with Docker Compose
- **Web Server**: Nginx (reverse proxy)

#### Python Libraries
- **Web Framework**: Flask/FastAPI
- **XML Parsing**: lxml or xml.etree
- **Database ORM**: SQLAlchemy
- **RightFax API**: requests library
- **File Watching**: watchdog
- **Task Queue** (for interval submissions): Celery with Redis
- **Testing**: pytest, unittest

### 6.2 Deployment Architecture

**REQ-TECH-001**: The system SHALL be fully containerized using Docker

**REQ-TECH-002**: The system SHALL use Docker Compose for multi-container orchestration

**REQ-TECH-003**: The system SHALL include the following containers:
- Web application (Python)
- PostgreSQL database
- Grafana
- Redis (for Celery task queue)
- Nginx (reverse proxy)

**REQ-TECH-004**: The system SHALL support deployment on Linux hosts (Ubuntu 20.04+, RHEL 8+)
- docker commands will use Docker Compose not docker-compose

**REQ-TECH-005**: The system SHALL persist data using Docker volumes for:
- PostgreSQL data
- Grafana configuration
- XML archive files
- Application logs

### 6.3 Configuration Management

**REQ-TECH-006**: The system SHALL use environment variables for all configuration including:
- Database connection strings
- RightFax server endpoints (API and FCL directory paths)
- RightFax API credentials
- XML monitoring directory path
- Timing parameters
- Logging levels

**REQ-TECH-007**: The system SHALL provide a sample `.env.example` file with all required variables documented

**REQ-TECH-008**: The system SHALL validate required configuration on startup and fail gracefully with clear error messages

### 6.4 Performance Requirements

**REQ-TECH-009**: The web UI SHALL respond to user interactions within 200ms

**REQ-TECH-010**: The system SHALL support submitting up to 100 faxes per minute via REST API

**REQ-TECH-011**: The system SHALL process XML files within 5 seconds of file arrival

**REQ-TECH-012**: The database SHALL handle time-series queries for 1M+ records within 2 seconds

**REQ-TECH-013**: Grafana dashboards SHALL load within 3 seconds for standard time ranges

### 6.5 Security Requirements

**REQ-TECH-014**: The system SHALL store RightFax API credentials encrypted or in secure environment variables

**REQ-TECH-015**: The web interface SHALL require authentication (basic auth minimum)

**REQ-TECH-016**: The system SHALL validate and sanitize all user inputs to prevent injection attacks

**REQ-TECH-017**: The system SHALL implement HTTPS for web interface in production deployments

**REQ-TECH-018**: The system SHALL implement appropriate file upload security measures (type validation, size limits, virus scanning optional)

### 6.6 Logging and Monitoring

**REQ-TECH-019**: The system SHALL implement structured logging (JSON format preferred)

**REQ-TECH-020**: The system SHALL log all critical operations including:
- Batch submissions start/completion
- XML file processing
- API calls to RightFax
- Database operations
- Errors and exceptions

**REQ-TECH-021**: The system SHALL implement log rotation to prevent disk space exhaustion

**REQ-TECH-022**: The system SHALL expose application health endpoint for monitoring

---

## System Architecture

### 7.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Environment                       │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │    Nginx     │────────▶│   Web App    │                 │
│  │ (Port 80/443)│         │   (Flask)    │                 │
│  └──────────────┘         └───────┬──────┘                 │
│                                    │                         │
│                          ┌─────────┼─────────┐              │
│                          │         │         │              │
│                    ┌─────▼───┐ ┌──▼────┐ ┌─▼────────┐      │
│                    │Postgres │ │ Redis │ │  Celery  │      │
│                    │   DB    │ │       │ │  Worker  │      │
│                    └─────┬───┘ └───────┘ └──────────┘      │
│                          │                                   │
│                    ┌─────▼───────┐                          │
│                    │   Grafana   │                          │
│                    │  (Port 3000)│                          │
│                    └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                             │
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐  ┌──────────┐   ┌──────────────┐
    │  RightFax    │  │ RightFax │   │  RightFax    │
    │   REST API   │  │   FCL    │   │  XML Output  │
    │              │  │   Drop   │   │  Directory   │
    └──────────────┘  └──────────┘   └──────────────┘
```

### 7.2 Component Descriptions

#### Web Application (Flask/FastAPI)
- Serves user interface
- Handles fax batch submissions
- Manages configuration
- Exposes REST API for status queries
- Schedules interval-based submissions via Celery

#### Celery Worker
- Processes interval-based fax submissions
- Executes background tasks
- Handles FCL file generation and API calls
- Manages retry logic

#### XML File Watcher
- Monitors RightFax XML output directory
- Triggers parsing on new file detection
- Archives processed files
- Handles concurrent file arrivals

#### Database Layer
- Stores submission logs
- Stores parsed completion data
- Maintains configuration data
- Provides time-series data for Grafana

#### Grafana
- Connects to PostgreSQL via PostgreSQL data source
- Renders dashboards with pre-configured panels
- Provides alerting capabilities
- Supports user customization

### 7.3 Data Flow

#### Fax Submission Flow
1. User configures batch parameters in web UI
2. Web app validates inputs and creates submission job
3. For interval-based: Celery tasks scheduled; For immediate: batch submitted directly
4. Application generates FCL files OR makes REST API calls
5. Submission details logged to PostgreSQL
6. Progress updates displayed in UI

#### Monitoring Flow
1. RightFax completes fax transmission and writes XML file
2. File watcher detects new XML file
3. Parser extracts metadata from XML
4. Data inserted into PostgreSQL with timestamp indexing
5. XML file moved to archive directory
6. Grafana queries database and updates dashboards
7. Metrics displayed in real-time

---

## Data Models

### 8.1 Database Schema

#### Table: `submission_batches`
Stores information about fax batch submissions.

```sql
CREATE TABLE submission_batches (
    id SERIAL PRIMARY KEY,
    batch_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    total_count INTEGER NOT NULL,
    submission_method VARCHAR(10) NOT NULL, -- 'FCL' or 'API'
    timing_type VARCHAR(20) NOT NULL, -- 'immediate' or 'interval'
    interval_seconds INTEGER, -- NULL if immediate
    recipient_phone VARCHAR(50) NOT NULL,
    recipient_name VARCHAR(255),
    account_name VARCHAR(100) NOT NULL,
    attachment_filename VARCHAR(255),
    status VARCHAR(20) NOT NULL, -- 'pending', 'in_progress', 'completed', 'cancelled', 'failed'
    submitted_count INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    notes TEXT
);
```

#### Table: `fax_submissions`
Stores individual fax submission records within batches.

```sql
CREATE TABLE fax_submissions (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER REFERENCES submission_batches(id),
    submitted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    submission_method VARCHAR(10) NOT NULL,
    rightfax_job_id VARCHAR(100), -- Job ID returned by RightFax
    recipient_phone VARCHAR(50) NOT NULL,
    recipient_name VARCHAR(255),
    account_name VARCHAR(100) NOT NULL,
    fcl_filename VARCHAR(255), -- If FCL method used
    api_response_code INTEGER, -- If API method used
    submission_status VARCHAR(20) NOT NULL, -- 'submitted', 'failed', 'pending_retry'
    error_message TEXT,
    CONSTRAINT fk_batch FOREIGN KEY (batch_id) REFERENCES submission_batches(id) ON DELETE CASCADE
);

CREATE INDEX idx_submissions_batch ON fax_submissions(batch_id);
CREATE INDEX idx_submissions_job_id ON fax_submissions(rightfax_job_id);
CREATE INDEX idx_submissions_timestamp ON fax_submissions(submitted_at);
```

#### Table: `fax_completions`
Stores parsed data from RightFax XML completion files.

```sql
CREATE TABLE fax_completions (
    id SERIAL PRIMARY KEY,
    rightfax_job_id VARCHAR(100) UNIQUE NOT NULL,
    submission_id INTEGER REFERENCES fax_submissions(id),
    submitted_at TIMESTAMP,
    completed_at TIMESTAMP NOT NULL,
    duration_seconds INTEGER,
    success BOOLEAN NOT NULL,
    error_code VARCHAR(50),
    error_description TEXT,
    recipient_phone VARCHAR(50),
    pages_transmitted INTEGER,
    account_name VARCHAR(100),
    call_attempts INTEGER,
    xml_filename VARCHAR(255),
    xml_parsed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    raw_xml TEXT -- Store complete XML for debugging
);

CREATE INDEX idx_completions_job_id ON fax_completions(rightfax_job_id);
CREATE INDEX idx_completions_completed_at ON fax_completions(completed_at);
CREATE INDEX idx_completions_success ON fax_completions(success);
CREATE INDEX idx_completions_account ON fax_completions(account_name);
```

#### Table: `system_config`
Stores application configuration and RightFax account details.

```sql
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    last_updated TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Example data
INSERT INTO system_config (config_key, config_value, description) VALUES
('rightfax_api_url', 'https://rightfax-server/api', 'RightFax REST API base URL'),
('rightfax_fcl_directory', '/mnt/rightfax/fcl', 'Directory for FCL file drops'),
('xml_monitor_directory', '/mnt/rightfax/xml', 'Directory to monitor for XML completion files');
```

#### Table: `rightfax_accounts`
Stores available RightFax accounts for selection.

```sql
CREATE TABLE rightfax_accounts (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(100) UNIQUE NOT NULL,
    account_id VARCHAR(50),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### 8.2 Data Relationships

- `submission_batches` → `fax_submissions` (one-to-many)
- `fax_submissions` → `fax_completions` (one-to-one, via rightfax_job_id)
- This allows correlation of submissions with completions for end-to-end tracking

---

## User Interface Requirements

### 9.1 Web Application UI

#### 9.1.1 Main Dashboard
- **Layout**: Single-page application with navigation sidebar
- **Sections**:
  - New Batch Submission form
  - Active Batches status
  - Recent Submissions history
  - Quick link to Grafana dashboard

#### 9.1.2 Batch Submission Form

**Layout Components**:
```
┌─────────────────────────────────────────────┐
│  New Fax Batch Submission                   │
├─────────────────────────────────────────────┤
│                                             │
│  Batch Name: [________________]             │
│                                             │
│  Number of Faxes: [____]                    │
│                                             │
│  Timing:                                    │
│    ○ Send Immediately                       │
│    ○ Send with Interval: [__] seconds       │
│                                             │
│  Recipient Phone: [________________]        │
│                                             │
│  Recipient Name: [________________]         │
│    □ Randomize names across batch           │
│                                             │
│  Account: [Dropdown ▼]                      │
│                                             │
│  Attachment: [Choose File]                  │
│    Selected: document.pdf (1.2 MB)          │
│                                             │
│  Submission Method:                         │
│    ○ FCL (File Drop)                        │
│    ○ REST API                               │
│                                             │
│  [Submit Batch]  [Save as Template]         │
│                                             │
└─────────────────────────────────────────────┘
```

**Validation Requirements**:
- Phone number: Format validation (configurable regex)
- File upload: Type and size validation
- Interval: Must be 1-300 seconds
- Batch count: Must be 1-10,000
- Real-time validation feedback

#### 9.1.3 Active Batches Panel

**Display Information**:
```
┌─────────────────────────────────────────────┐
│  Active Batches                             │
├─────────────────────────────────────────────┤
│                                             │
│  Batch: Load Test 2025-11-14 14:30         │
│  Status: In Progress                        │
│  Progress: ████████░░░░ 42/100 (42%)       │
│  Rate: 2.5 faxes/min                        │
│  ETA: 23 minutes                            │
│  [Cancel] [View Details]                    │
│                                             │
│  ─────────────────────────────────────────  │
│                                             │
│  Batch: API Test High Volume               │
│  Status: Queued                             │
│  Progress: ░░░░░░░░░░░░ 0/500              │
│  Starts: 15:00                              │
│  [Cancel] [View Details]                    │
│                                             │
└─────────────────────────────────────────────┘
```

#### 9.1.4 Recent Submissions History

**Table Columns**:
- Batch Name
- Timestamp
- Count
- Method (FCL/API)
- Status (Completed/Failed/Cancelled)
- Success Rate (%)
- Actions (View Details, Duplicate)

**Features**:
- Pagination (25/50/100 per page)
- Sorting by column
- Filtering by date range, method, status
- Export to CSV

#### 9.1.5 Batch Details View

**Information Displayed**:
- Complete batch configuration
- Individual submission status for each fax
- Correlated completion data (when available)
- Error messages for failed submissions
- Timeline visualization
- Export options

### 9.2 Grafana Dashboard UI

#### 9.2.1 Dashboard Layout

**Dashboard Name**: "RightFax Performance Monitoring"

**Panel Configuration** (suggested 6-panel layout):

**Row 1**:
1. **Jobs Per Minute (Graph)**
   - Time series line chart
   - Y-axis: Jobs/minute
   - Shows real-time throughput

2. **Success Rate (Gauge)**
   - Percentage gauge
   - Color thresholds: Red <80%, Yellow 80-95%, Green >95%

**Row 2**:
3. **Concurrent Calls (Graph)**
   - Area chart showing concurrent active calls over time
   - Highlights peak concurrency

4. **Average Call Duration (Graph)**
   - Multiple series: p50, p90, p99 percentiles
   - Time series visualization

**Row 3**:
5. **Call Attempts Distribution (Bar Chart)**
   - X-axis: Number of attempts (1, 2, 3, 4+)
   - Y-axis: Count
   - Shows first-call success vs retries

6. **Error Code Distribution (Pie Chart)**
   - Breakdown of error types
   - Filterable by time range

**Row 4 (Full Width)**:
7. **Detailed Job Table**
   - Recent completions with drill-down capability
   - Columns: Job ID, Time, Duration, Status, Phone, Account, Pages
   - Sortable and filterable

#### 9.2.2 Variables and Filters

**Dashboard Variables**:
- `account`: Dropdown for account filtering
- `time_range`: Time range selector
- `status`: Filter by success/failure
- `min_duration`: Filter by minimum call duration

#### 9.2.3 Alerting Configuration

**Suggested Alerts**:
1. Error rate exceeds 10% over 5-minute window
2. Average duration exceeds 120 seconds over 10-minute window
3. No completions received for 10 minutes (system health)

---

## Integration Specifications

### 10.1 RightFax FCL Integration

#### 10.1.1 FCL File Format

FCL (Fax Command Language) files are plain text files with specific formatting. Below is a sample:

**Example FCL File** (`fax_20251114143022_001.fcl`):
```
{{begin}}

{{fax 904-202-0999}}
{{attach C:\CustomFolder\Attachments\RightFax_Connect_Portal_Quick_Reference.pdf}}

{{winsecid AUGUST}}

{{end}}
```
Full FCL File docs are in the     /docs/OpenText Fax CE 24.4 - Integration Module Administrator Guide.pdf


**REQ-FCL-001**: The system SHALL generate FCL files with unique filenames using format: `fax_<timestamp>_<sequence>.fcl`

**REQ-FCL-002**: The system SHALL write FCL files atomically to prevent partial reads by RightFax

**REQ-FCL-003**: The system SHALL support the following FCL parameters:
- `TO`: Recipient phone number (required)
- `NAME`: Recipient name (optional)
- `ACCOUNT`: Sending account (required)
- `COVERPAGE`: Cover page template (optional)
- `FILE`: Attachment file path (required)
- `SUBJECT`: Fax subject line (optional)
- `PRIORITY`: Priority level (optional: LOW, NORMAL, HIGH)

**REQ-FCL-004**: The system SHALL validate that attachment files exist and are accessible before generating FCL

**REQ-FCL-005**: The system SHALL log FCL file generation with filename and parameters for troubleshooting

#### 10.1.2 FCL Directory Configuration

**REQ-FCL-006**: The FCL drop directory SHALL be configurable via environment variable

**REQ-FCL-007**: The system SHALL verify write permissions to FCL directory on startup

**REQ-FCL-008**: The system SHALL handle FCL directory being temporarily unavailable (network mount scenarios)

### 10.2 RightFax REST API Integration

#### 10.2.1 API Documentation Reference

The RightFax REST API documentation and sample code are located in the `docs` folder. The integration SHALL reference this documentation for:
- Authentication methods
- Endpoint specifications
- Request/response formats
- Error codes

**REQ-API-001**: The system SHALL implement authentication per RightFax API specifications (likely OAuth 2.0 or API key)

**REQ-API-002**: The system SHALL support the fax submission endpoint as documented in the API guide

**REQ-API-003**: The system SHALL handle API rate limiting with exponential backoff

#### 10.2.2 API Request Format

**Typical API Submission Request** (example - verify with actual docs):
```http
POST /api/v2/faxes HTTP/1.1
Host: rightfax-server.example.com
Authorization: Bearer <token>
Content-Type: application/json

{
    "recipient": {
        "name": "John Smith",
        "number": "+14155551234"
    },
    "sender": {
        "account": "TestAccount01"
    },
    "document": {
        "base64": "<base64_encoded_document>",
        "filename": "document.pdf",
        "contentType": "application/pdf"
    },
    "options": {
        "coverPage": "Standard",
        "priority": "NORMAL"
    }
}
```

**REQ-API-004**: The system SHALL encode attachments as base64 for API submissions

**REQ-API-005**: The system SHALL extract and store the job ID from API responses

**REQ-API-006**: The system SHALL handle API error responses and log error details

#### 10.2.3 API Response Handling

**REQ-API-007**: The system SHALL parse successful API responses to extract:
- Job ID
- Submission timestamp
- Any status information

**REQ-API-008**: The system SHALL map API error codes to user-friendly messages

**REQ-API-009**: The system SHALL implement retry logic for transient errors (timeouts, 5xx errors)

**REQ-API-010**: The system SHALL fail gracefully for permanent errors (4xx errors) without retrying

### 10.3 XML Completion File Processing

#### 10.3.1 XML File Format

RightFax writes XML completion files containing transmission metadata. The exact schema will vary by RightFax version, but typically includes:

**Example XML Structure** is in the /samples directory


**REQ-XML-001**: The system SHALL parse XML files according to the schema provided by RightFax

**REQ-XML-002**: The system SHALL handle missing optional fields gracefully

**REQ-XML-003**: The system SHALL validate required fields are present before storing data

**REQ-XML-004**: The system SHALL store the complete raw XML for debugging purposes

#### 10.3.2 XML Monitoring

**REQ-XML-005**: The system SHALL use file system watching (e.g., inotify on Linux) for efficient file detection

**REQ-XML-006**: The system SHALL handle XML files written incrementally (wait for write completion)

**REQ-XML-007**: The system SHALL process XML files in order of creation timestamp

**REQ-XML-008**: The system SHALL archive processed XML files with date-based directory structure

**REQ-XML-009**: The system SHALL implement configurable retention for archived XML (default: 90 days)

#### 10.3.3 Error Handling

**REQ-XML-010**: The system SHALL log XML parsing errors with filename and error details

**REQ-XML-011**: The system SHALL move malformed XML files to an error directory for manual review

**REQ-XML-012**: The system SHALL continue processing subsequent files if one file fails to parse

**REQ-XML-013**: The system SHALL alert administrators (via log) if XML processing falls behind by >5 minutes

### 10.4 PostgreSQL and Grafana Integration

**REQ-GRAF-001**: Grafana SHALL connect to PostgreSQL using the PostgreSQL data source plugin

**REQ-GRAF-002**: The system SHALL provide a provisioned dashboard configuration file for automatic setup

**REQ-GRAF-003**: Dashboard queries SHALL use indexed columns for performance

**REQ-GRAF-004**: The system SHALL document all Grafana SQL queries for custom dashboard creation

**Example Grafana Query** (Jobs per minute):
```sql
SELECT
  time_bucket('1 minute', completed_at) AS time,
  COUNT(*) AS jobs_per_minute
FROM fax_completions
WHERE completed_at >= NOW() - INTERVAL '1 hour'
GROUP BY time
ORDER BY time;
```

**REQ-GRAF-005**: The system SHALL include TimescaleDB extension (optional) for enhanced time-series performance

---

## Success Metrics

### 11.1 User Adoption Metrics
- Number of test batches submitted per week
- Diversity of users running tests
- Repeat usage rate

### 11.2 Technical Performance Metrics
- Submission success rate (target: >99%)
- XML processing latency (target: <5 seconds)
- Dashboard query response time (target: <2 seconds)
- System uptime (target: >99.5%)

### 11.3 Business Value Metrics
- Time saved vs. manual testing methods (baseline vs. new tool)
- Number of capacity planning decisions informed by data
- Number of performance issues identified and resolved
- RightFax infrastructure optimization improvements

### 11.4 Data Quality Metrics
- XML parsing success rate (target: 100%)
- Data completeness in database
- Job correlation rate (submissions → completions)

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
**Deliverables**:
- Docker environment setup
- Database schema implementation
- Basic web application framework
- Configuration management
- Development environment documentation

**Success Criteria**:
- Docker containers running
- Database accessible
- Web app serves basic UI
- Configuration loads from environment

### Phase 2: Fax Submission Tool (Weeks 3-4)
**Deliverables**:
- Fax submission UI
- FCL file generation
- REST API integration
- Batch management
- Progress tracking

**Success Criteria**:
- Submit test batches via both methods
- FCL files correctly formatted
- API calls successful
- Batch status tracked in database

### Phase 3: XML Processing (Week 5)
**Deliverables**:
- File watcher implementation
- XML parser
- Database storage
- Archive management
- Error handling

**Success Criteria**:
- XML files detected within 5 seconds
- Data parsed and stored correctly
- Malformed files handled gracefully
- Archive system operational

### Phase 4: Grafana Dashboard (Week 6)
**Deliverables**:
- Grafana configuration
- Dashboard panels
- SQL queries optimized
- Alert configuration
- Documentation

**Success Criteria**:
- All required metrics visible
- Dashboards load quickly
- Data refreshes in real-time
- Alerts trigger correctly

### Phase 5: Testing & Refinement (Week 7-8)
**Deliverables**:
- End-to-end testing
- Load testing (handle 1000+ submissions)
- Performance optimization
- Bug fixes
- User documentation

**Success Criteria**:
- System handles target load
- All workflows tested
- Known issues resolved
- Documentation complete

### Phase 6: Deployment & Training (Week 9)
**Deliverables**:
- Production deployment
- User training sessions
- Operations runbook
- Monitoring setup

**Success Criteria**:
- System deployed in production
- Users trained and comfortable
- Monitoring active
- Support process established

---

## Risks and Mitigations

### 13.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| RightFax API changes/inconsistencies | High | Medium | Version API integration, maintain flexibility, test with actual RightFax instance early |
| XML schema variations across RightFax versions | Medium | High | Implement flexible XML parsing, log unknown fields, support multiple schema versions |
| Network latency to RightFax server | Medium | Medium | Implement timeout handling, queue-based submission, retry logic |
| Docker volume permissions issues | Low | Medium | Document permission requirements, implement permission checks on startup |
| Database performance with large datasets | Medium | Low | Implement proper indexing, consider partitioning, use TimescaleDB if needed |
| FCL directory mount failures | Medium | Medium | Implement connection retry, clear error messages, health checks |

### 13.2 Integration Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| RightFax not writing XML files as expected | High | Low | Test with actual RightFax early, implement monitoring for missing files |
| Attachment file size limits | Medium | Medium | Document limits clearly, validate file sizes before submission |
| Account permissions in RightFax | Medium | Medium | Implement account validation, clear error messages for permission issues |
| Concurrent access to FCL directory | Low | Low | Implement file locking, use atomic write operations |

### 13.3 Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Users submitting excessive test loads | High | Medium | Implement rate limiting, batch size limits, approval workflow for large tests |
| Disk space exhaustion from XML archives | Medium | Medium | Implement automatic cleanup, monitoring, configurable retention |
| Lack of user adoption | Medium | Medium | Provide training, documentation, demonstrate value with case studies |
| Insufficient documentation | Medium | Low | Prioritize documentation, include runbooks and troubleshooting guides |

---

## Future Enhancements

### 14.1 Short-term Enhancements (3-6 months)

1. **Template Library**: Pre-configured batch templates for common test scenarios
2. **Scheduled Testing**: Cron-like scheduling for recurring tests
3. **Enhanced Reporting**: PDF export of test results with charts
4. **Account Rotation**: Distribute faxes across multiple accounts automatically
5. **Phone Number Lists**: Support uploading CSV of recipient numbers
6. **Comparison Mode**: Compare performance between two time periods or configurations

### 14.2 Medium-term Enhancements (6-12 months)

1. **Multi-Server Support**: Test multiple RightFax servers simultaneously
2. **Advanced Analytics**: Machine learning-based anomaly detection
3. **Capacity Prediction**: Predict system capacity based on historical data
4. **Integration with Ticketing**: Auto-create tickets for failed tests
5. **Mobile App**: Native mobile app for monitoring on the go
6. **Webhook Notifications**: Real-time notifications via Slack/Teams/email

### 14.3 Long-term Vision (12+ months)

1. **Multi-Tenant Architecture**: Support multiple organizations/customers
2. **AI-Powered Optimization**: Recommendations for optimal test parameters
3. **Distributed Testing**: Support distributed load generation
4. **Cloud Deployment**: Kubernetes-based cloud-native deployment
5. **Marketplace**: Community-contributed templates and dashboards
6. **Full Test Automation Framework**: API-driven testing for CI/CD integration

---

## Appendices

### Appendix A: Glossary

- **FCL (Fax Command Language)**: RightFax proprietary format for fax submission via file drop
- **Batch**: A group of faxes submitted together with the same configuration
- **Job ID**: Unique identifier assigned by RightFax to each fax transmission
- **Completion File**: XML file written by RightFax upon fax transmission completion
- **Interval Submission**: Fax submission with time delays between individual faxes

### Appendix B: References

- RightFax REST API Documentation (see `docs/` folder)
- RightFax FCL Reference Guide
- Docker Documentation: https://docs.docker.com
- Grafana Documentation: https://grafana.com/docs
- PostgreSQL Documentation: https://www.postgresql.org/docs

### Appendix C: Sample Configuration

**Sample `.env` file**:
```bash
# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=rightfax_testing
POSTGRES_USER=admin
POSTGRES_PASSWORD=<secure_password>

# RightFax Configuration
RIGHTFAX_API_URL=https://rightfax.example.com/api/v2
RIGHTFAX_API_KEY=<api_key>
RIGHTFAX_FCL_DIRECTORY=/mnt/rightfax/fcl
RIGHTFAX_XML_DIRECTORY=/mnt/rightfax/xml

# Application Configuration
FLASK_SECRET_KEY=<random_secret_key>
APP_PORT=5000
LOG_LEVEL=INFO

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Grafana Configuration
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=<secure_password>
```

### Appendix D: Database Indexes for Performance

```sql
-- Additional indexes for optimal query performance

-- For time-range queries
CREATE INDEX idx_completions_time_range ON fax_completions(completed_at DESC, success);

-- For account-based filtering
CREATE INDEX idx_completions_account_time ON fax_completions(account_name, completed_at DESC);

-- For duration analysis
CREATE INDEX idx_completions_duration ON fax_completions(duration_seconds) WHERE success = true;

-- For job correlation
CREATE INDEX idx_submissions_job_lookup ON fax_submissions(rightfax_job_id, batch_id);

-- For batch status queries
CREATE INDEX idx_batches_status_time ON submission_batches(status, created_at DESC);
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-14 | August Startz | Initial PRD creation |

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | | | |
| Technical Lead | | | |
| Stakeholder | | | |

---

**END OF DOCUMENT**

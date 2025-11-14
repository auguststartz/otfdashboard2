-- RightFax Testing & Monitoring Platform Database Schema
-- Version: 1.0
-- Date: 2025-11-14

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: submission_batches
-- Stores information about fax batch submissions
CREATE TABLE IF NOT EXISTS submission_batches (
    id SERIAL PRIMARY KEY,
    batch_name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    total_count INTEGER NOT NULL,
    submission_method VARCHAR(10) NOT NULL CHECK (submission_method IN ('FCL', 'API')),
    timing_type VARCHAR(20) NOT NULL CHECK (timing_type IN ('immediate', 'interval')),
    interval_seconds INTEGER,
    recipient_phone VARCHAR(50) NOT NULL,
    recipient_name VARCHAR(255),
    account_name VARCHAR(100) NOT NULL,
    attachment_filename VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled', 'failed')),
    submitted_count INTEGER DEFAULT 0,
    completed_at TIMESTAMP,
    notes TEXT
);

-- Table: fax_submissions
-- Stores individual fax submission records within batches
CREATE TABLE IF NOT EXISTS fax_submissions (
    id SERIAL PRIMARY KEY,
    batch_id INTEGER REFERENCES submission_batches(id) ON DELETE CASCADE,
    submitted_at TIMESTAMP NOT NULL DEFAULT NOW(),
    submission_method VARCHAR(10) NOT NULL CHECK (submission_method IN ('FCL', 'API')),
    rightfax_job_id VARCHAR(100),
    recipient_phone VARCHAR(50) NOT NULL,
    recipient_name VARCHAR(255),
    account_name VARCHAR(100) NOT NULL,
    fcl_filename VARCHAR(255),
    api_response_code INTEGER,
    submission_status VARCHAR(20) NOT NULL DEFAULT 'submitted' CHECK (submission_status IN ('submitted', 'failed', 'pending_retry')),
    error_message TEXT
);

-- Table: fax_completions
-- Stores parsed data from RightFax XML completion files
CREATE TABLE IF NOT EXISTS fax_completions (
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
    raw_xml TEXT,
    -- Additional fields from XML
    fax_handle VARCHAR(50),
    fax_channel VARCHAR(10),
    job_create_time TIMESTAMP,
    fax_create_time TIMESTAMP,
    fax_server VARCHAR(100),
    job_type VARCHAR(50),
    disposition INTEGER,
    term_stat INTEGER,
    good_page_count INTEGER,
    bad_page_count INTEGER
);

-- Table: system_config
-- Stores application configuration
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    last_updated TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Table: rightfax_accounts
-- Stores available RightFax accounts for selection
CREATE TABLE IF NOT EXISTS rightfax_accounts (
    id SERIAL PRIMARY KEY,
    account_name VARCHAR(100) UNIQUE NOT NULL,
    account_id VARCHAR(50),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_submissions_batch ON fax_submissions(batch_id);
CREATE INDEX IF NOT EXISTS idx_submissions_job_id ON fax_submissions(rightfax_job_id);
CREATE INDEX IF NOT EXISTS idx_submissions_timestamp ON fax_submissions(submitted_at);

CREATE INDEX IF NOT EXISTS idx_completions_job_id ON fax_completions(rightfax_job_id);
CREATE INDEX IF NOT EXISTS idx_completions_completed_at ON fax_completions(completed_at);
CREATE INDEX IF NOT EXISTS idx_completions_success ON fax_completions(success);
CREATE INDEX IF NOT EXISTS idx_completions_account ON fax_completions(account_name);
CREATE INDEX IF NOT EXISTS idx_completions_time_range ON fax_completions(completed_at DESC, success);
CREATE INDEX IF NOT EXISTS idx_completions_account_time ON fax_completions(account_name, completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_completions_duration ON fax_completions(duration_seconds) WHERE success = true;

CREATE INDEX IF NOT EXISTS idx_submissions_job_lookup ON fax_submissions(rightfax_job_id, batch_id);
CREATE INDEX IF NOT EXISTS idx_batches_status_time ON submission_batches(status, created_at DESC);

-- Insert default configuration values
INSERT INTO system_config (config_key, config_value, description) VALUES
    ('rightfax_api_url', '', 'RightFax REST API base URL'),
    ('rightfax_fcl_directory', '/mnt/rightfax/fcl', 'Directory for FCL file drops'),
    ('xml_monitor_directory', '/mnt/rightfax/xml', 'Directory to monitor for XML completion files'),
    ('xml_retention_days', '90', 'Number of days to retain archived XML files')
ON CONFLICT (config_key) DO NOTHING;

-- Insert sample RightFax accounts (customize as needed)
INSERT INTO rightfax_accounts (account_name, account_id, description, is_active) VALUES
    ('API', 'API', 'API Test Account', true),
    ('TESTACCOUNT', 'TEST01', 'Test Account 01', true)
ON CONFLICT (account_name) DO NOTHING;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin;

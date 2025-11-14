"""
SQLAlchemy Models for RightFax Testing Platform
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, CheckConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database import Base


class SubmissionBatch(Base):
    """Model for submission_batches table"""
    __tablename__ = 'submission_batches'

    id = Column(Integer, primary_key=True)
    batch_name = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(100))
    total_count = Column(Integer, nullable=False)
    submission_method = Column(String(10), nullable=False)
    timing_type = Column(String(20), nullable=False)
    interval_seconds = Column(Integer)
    recipient_phone = Column(String(50), nullable=False)
    recipient_name = Column(String(255))
    account_name = Column(String(100), nullable=False)
    attachment_filename = Column(String(255))
    status = Column(String(20), nullable=False, default='pending')
    submitted_count = Column(Integer, default=0)
    completed_at = Column(DateTime)
    notes = Column(Text)

    # Relationships
    submissions = relationship('FaxSubmission', back_populates='batch', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint("submission_method IN ('FCL', 'API')", name='check_submission_method'),
        CheckConstraint("timing_type IN ('immediate', 'interval')", name='check_timing_type'),
        CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'cancelled', 'failed')", name='check_status'),
        Index('idx_batches_status_time', 'status', 'created_at'),
    )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'batch_name': self.batch_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by,
            'total_count': self.total_count,
            'submission_method': self.submission_method,
            'timing_type': self.timing_type,
            'interval_seconds': self.interval_seconds,
            'recipient_phone': self.recipient_phone,
            'recipient_name': self.recipient_name,
            'account_name': self.account_name,
            'attachment_filename': self.attachment_filename,
            'status': self.status,
            'submitted_count': self.submitted_count,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'notes': self.notes
        }


class FaxSubmission(Base):
    """Model for fax_submissions table"""
    __tablename__ = 'fax_submissions'

    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey('submission_batches.id', ondelete='CASCADE'))
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    submission_method = Column(String(10), nullable=False)
    rightfax_job_id = Column(String(100))
    recipient_phone = Column(String(50), nullable=False)
    recipient_name = Column(String(255))
    account_name = Column(String(100), nullable=False)
    fcl_filename = Column(String(255))
    api_response_code = Column(Integer)
    submission_status = Column(String(20), nullable=False, default='submitted')
    error_message = Column(Text)

    # Relationships
    batch = relationship('SubmissionBatch', back_populates='submissions')
    completion = relationship('FaxCompletion', back_populates='submission', uselist=False)

    __table_args__ = (
        CheckConstraint("submission_method IN ('FCL', 'API')", name='check_fax_submission_method'),
        CheckConstraint("submission_status IN ('submitted', 'failed', 'pending_retry')", name='check_submission_status'),
        Index('idx_submissions_batch', 'batch_id'),
        Index('idx_submissions_job_id', 'rightfax_job_id'),
        Index('idx_submissions_timestamp', 'submitted_at'),
        Index('idx_submissions_job_lookup', 'rightfax_job_id', 'batch_id'),
    )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'submission_method': self.submission_method,
            'rightfax_job_id': self.rightfax_job_id,
            'recipient_phone': self.recipient_phone,
            'recipient_name': self.recipient_name,
            'account_name': self.account_name,
            'fcl_filename': self.fcl_filename,
            'api_response_code': self.api_response_code,
            'submission_status': self.submission_status,
            'error_message': self.error_message
        }


class FaxCompletion(Base):
    """Model for fax_completions table"""
    __tablename__ = 'fax_completions'

    id = Column(Integer, primary_key=True)
    rightfax_job_id = Column(String(100), unique=True, nullable=False)
    submission_id = Column(Integer, ForeignKey('fax_submissions.id'))
    submitted_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer)
    success = Column(Boolean, nullable=False)
    error_code = Column(String(50))
    error_description = Column(Text)
    recipient_phone = Column(String(50))
    pages_transmitted = Column(Integer)
    account_name = Column(String(100))
    call_attempts = Column(Integer)
    xml_filename = Column(String(255))
    xml_parsed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    raw_xml = Column(Text)

    # Additional fields from XML
    fax_handle = Column(String(50))
    fax_channel = Column(String(10))
    job_create_time = Column(DateTime)
    fax_create_time = Column(DateTime)
    fax_server = Column(String(100))
    job_type = Column(String(50))
    disposition = Column(Integer)
    term_stat = Column(Integer)
    good_page_count = Column(Integer)
    bad_page_count = Column(Integer)

    # Relationships
    submission = relationship('FaxSubmission', back_populates='completion')

    __table_args__ = (
        Index('idx_completions_job_id', 'rightfax_job_id'),
        Index('idx_completions_completed_at', 'completed_at'),
        Index('idx_completions_success', 'success'),
        Index('idx_completions_account', 'account_name'),
        Index('idx_completions_time_range', 'completed_at', 'success'),
        Index('idx_completions_account_time', 'account_name', 'completed_at'),
    )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'rightfax_job_id': self.rightfax_job_id,
            'submission_id': self.submission_id,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'success': self.success,
            'error_code': self.error_code,
            'error_description': self.error_description,
            'recipient_phone': self.recipient_phone,
            'pages_transmitted': self.pages_transmitted,
            'account_name': self.account_name,
            'call_attempts': self.call_attempts,
            'xml_filename': self.xml_filename,
            'fax_handle': self.fax_handle,
            'fax_channel': self.fax_channel,
            'job_type': self.job_type,
            'disposition': self.disposition,
            'term_stat': self.term_stat,
            'good_page_count': self.good_page_count,
            'bad_page_count': self.bad_page_count
        }


class SystemConfig(Base):
    """Model for system_config table"""
    __tablename__ = 'system_config'

    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text)
    description = Column(Text)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'description': self.description,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class RightFaxAccount(Base):
    """Model for rightfax_accounts table"""
    __tablename__ = 'rightfax_accounts'

    id = Column(Integer, primary_key=True)
    account_name = Column(String(100), unique=True, nullable=False)
    account_id = Column(String(50))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'account_name': self.account_name,
            'account_id': self.account_id,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

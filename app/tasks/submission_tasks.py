"""
Celery tasks for fax submission
"""
import time
import logging
from app.celery_app import celery
from app.database import SessionLocal
from app.models import SubmissionBatch, FaxSubmission
from app.services.fcl_generator import FCLGenerator
from app.services.rightfax_api import RightFaxAPIClient

logger = logging.getLogger(__name__)


@celery.task(name='submit_batch')
def submit_batch(batch_id):
    """
    Submit a batch of faxes
    """
    db = SessionLocal()
    try:
        batch = db.query(SubmissionBatch).filter(SubmissionBatch.id == batch_id).first()
        if not batch:
            logger.error(f"Batch {batch_id} not found")
            return

        # Update status to in_progress
        batch.status = 'in_progress'
        db.commit()

        logger.info(f"Starting submission for batch {batch_id}: {batch.total_count} faxes")

        if batch.submission_method == 'FCL':
            submit_via_fcl(batch, db)
        elif batch.submission_method == 'API':
            submit_via_api(batch, db)

        # Update status to completed
        batch.status = 'completed'
        batch.submitted_count = batch.total_count
        db.commit()

        logger.info(f"Batch {batch_id} submission completed")

    except Exception as e:
        logger.error(f"Error submitting batch {batch_id}: {e}")
        batch.status = 'failed'
        db.commit()
    finally:
        db.close()


def submit_via_fcl(batch: SubmissionBatch, db):
    """Submit faxes using FCL file method"""
    fcl_gen = FCLGenerator()

    for i in range(batch.total_count):
        try:
            # Generate FCL file
            fcl_filename = fcl_gen.generate_fcl(
                recipient_phone=batch.recipient_phone,
                recipient_name=batch.recipient_name or f"Recipient {i+1}",
                account_name=batch.account_name,
                attachment_filename=batch.attachment_filename
            )

            # Create submission record
            submission = FaxSubmission(
                batch_id=batch.id,
                submission_method='FCL',
                recipient_phone=batch.recipient_phone,
                recipient_name=batch.recipient_name,
                account_name=batch.account_name,
                fcl_filename=fcl_filename,
                submission_status='submitted'
            )
            db.add(submission)

            # Update batch count
            batch.submitted_count = i + 1
            db.commit()

            logger.debug(f"Submitted fax {i+1}/{batch.total_count} via FCL: {fcl_filename}")

            # Apply interval if needed
            if batch.timing_type == 'interval' and batch.interval_seconds:
                if i < batch.total_count - 1:  # Don't sleep after last fax
                    time.sleep(batch.interval_seconds)

        except Exception as e:
            logger.error(f"Error submitting fax {i+1} via FCL: {e}")
            submission = FaxSubmission(
                batch_id=batch.id,
                submission_method='FCL',
                recipient_phone=batch.recipient_phone,
                recipient_name=batch.recipient_name,
                account_name=batch.account_name,
                submission_status='failed',
                error_message=str(e)
            )
            db.add(submission)
            db.commit()


def submit_via_api(batch: SubmissionBatch, db):
    """Submit faxes using RightFax REST API"""
    api_client = RightFaxAPIClient()

    for i in range(batch.total_count):
        try:
            # Submit via API
            response = api_client.submit_fax(
                recipient_phone=batch.recipient_phone,
                recipient_name=batch.recipient_name or f"Recipient {i+1}",
                account_name=batch.account_name,
                attachment_path=batch.attachment_filename
            )

            # Create submission record
            submission = FaxSubmission(
                batch_id=batch.id,
                submission_method='API',
                recipient_phone=batch.recipient_phone,
                recipient_name=batch.recipient_name,
                account_name=batch.account_name,
                rightfax_job_id=response.get('job_id'),
                api_response_code=response.get('status_code'),
                submission_status='submitted'
            )
            db.add(submission)

            # Update batch count
            batch.submitted_count = i + 1
            db.commit()

            logger.debug(f"Submitted fax {i+1}/{batch.total_count} via API: {response.get('job_id')}")

            # Apply interval if needed
            if batch.timing_type == 'interval' and batch.interval_seconds:
                if i < batch.total_count - 1:
                    time.sleep(batch.interval_seconds)

        except Exception as e:
            logger.error(f"Error submitting fax {i+1} via API: {e}")
            submission = FaxSubmission(
                batch_id=batch.id,
                submission_method='API',
                recipient_phone=batch.recipient_phone,
                recipient_name=batch.recipient_name,
                account_name=batch.account_name,
                submission_status='failed',
                error_message=str(e)
            )
            db.add(submission)
            db.commit()


@celery.task(name='submit_single_fax')
def submit_single_fax(batch_id, index):
    """
    Submit a single fax (for interval-based submissions)
    This allows better control over scheduling
    """
    db = SessionLocal()
    try:
        batch = db.query(SubmissionBatch).filter(SubmissionBatch.id == batch_id).first()
        if not batch:
            return

        if batch.submission_method == 'FCL':
            fcl_gen = FCLGenerator()
            fcl_filename = fcl_gen.generate_fcl(
                recipient_phone=batch.recipient_phone,
                recipient_name=batch.recipient_name or f"Recipient {index}",
                account_name=batch.account_name,
                attachment_filename=batch.attachment_filename
            )

            submission = FaxSubmission(
                batch_id=batch.id,
                submission_method='FCL',
                recipient_phone=batch.recipient_phone,
                recipient_name=batch.recipient_name,
                account_name=batch.account_name,
                fcl_filename=fcl_filename,
                submission_status='submitted'
            )
        else:  # API
            api_client = RightFaxAPIClient()
            response = api_client.submit_fax(
                recipient_phone=batch.recipient_phone,
                recipient_name=batch.recipient_name or f"Recipient {index}",
                account_name=batch.account_name,
                attachment_path=batch.attachment_filename
            )

            submission = FaxSubmission(
                batch_id=batch.id,
                submission_method='API',
                recipient_phone=batch.recipient_phone,
                recipient_name=batch.recipient_name,
                account_name=batch.account_name,
                rightfax_job_id=response.get('job_id'),
                api_response_code=response.get('status_code'),
                submission_status='submitted'
            )

        db.add(submission)
        batch.submitted_count += 1
        db.commit()

    except Exception as e:
        logger.error(f"Error in submit_single_fax: {e}")
        db.rollback()
    finally:
        db.close()

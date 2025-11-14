"""
API Routes for RightFax Testing Platform
"""
from flask import Blueprint, request, jsonify, current_app
from app.database import SessionLocal
from app.models import (
    SubmissionBatch, FaxSubmission, FaxCompletion,
    RightFaxAccount, SystemConfig
)
from sqlalchemy import desc, func
from datetime import datetime, timedelta

bp = Blueprint('api', __name__, url_prefix='/api')


def get_celery():
    """Get Celery instance - import here to avoid circular imports"""
    from app.tasks.submission_tasks import submit_batch
    return submit_batch


@bp.route('/batches', methods=['GET'])
def get_batches():
    """Get all submission batches with optional filtering"""
    db = SessionLocal()
    try:
        # Query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        status = request.args.get('status')

        query = db.query(SubmissionBatch).order_by(desc(SubmissionBatch.created_at))

        if status:
            query = query.filter(SubmissionBatch.status == status)

        total = query.count()
        batches = query.limit(limit).offset(offset).all()

        return jsonify({
            'batches': [batch.to_dict() for batch in batches],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching batches: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/batches/<int:batch_id>', methods=['GET'])
def get_batch(batch_id):
    """Get a specific batch by ID"""
    db = SessionLocal()
    try:
        batch = db.query(SubmissionBatch).filter(SubmissionBatch.id == batch_id).first()
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        # Include submission details
        submissions = db.query(FaxSubmission).filter(
            FaxSubmission.batch_id == batch_id
        ).all()

        return jsonify({
            'batch': batch.to_dict(),
            'submissions': [s.to_dict() for s in submissions]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching batch {batch_id}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/batches', methods=['POST'])
def create_batch():
    """Create a new fax submission batch"""
    db = SessionLocal()
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['total_count', 'submission_method', 'timing_type',
                          'recipient_phone', 'account_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Create batch record
        batch = SubmissionBatch(
            batch_name=data.get('batch_name'),
            created_by=data.get('created_by', 'system'),
            total_count=data['total_count'],
            submission_method=data['submission_method'],
            timing_type=data['timing_type'],
            interval_seconds=data.get('interval_seconds'),
            recipient_phone=data['recipient_phone'],
            recipient_name=data.get('recipient_name'),
            account_name=data['account_name'],
            attachment_filename=data.get('attachment_filename'),
            status='pending',
            notes=data.get('notes')
        )

        db.add(batch)
        db.commit()
        db.refresh(batch)

        current_app.logger.info(f"Created batch {batch.id}: {batch.batch_name}")

        # Trigger Celery task to start submitting faxes
        try:
            submit_batch_task = get_celery()
            task = submit_batch_task.delay(batch.id)
            current_app.logger.info(f"Triggered Celery task {task.id} for batch {batch.id}")
        except Exception as e:
            current_app.logger.error(f"Error triggering Celery task for batch {batch.id}: {e}")
            # Don't fail the request - batch is created, just log the error
            # User can manually trigger or retry

        return jsonify({
            'message': 'Batch created successfully',
            'batch': batch.to_dict()
        }), 201

    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error creating batch: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/batches/<int:batch_id>/trigger', methods=['POST'])
def trigger_batch(batch_id):
    """Manually trigger a batch submission (for pending or failed batches)"""
    db = SessionLocal()
    try:
        batch = db.query(SubmissionBatch).filter(SubmissionBatch.id == batch_id).first()
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        if batch.status not in ['pending', 'failed', 'cancelled']:
            return jsonify({'error': f'Cannot trigger batch with status: {batch.status}'}), 400

        # Reset batch to pending
        batch.status = 'pending'
        batch.submitted_count = 0
        db.commit()

        # Trigger Celery task
        submit_batch_task = get_celery()
        task = submit_batch_task.delay(batch.id)

        current_app.logger.info(f"Manually triggered Celery task {task.id} for batch {batch_id}")

        return jsonify({
            'message': 'Batch submission triggered',
            'task_id': task.id,
            'batch_id': batch_id
        }), 200

    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error triggering batch {batch_id}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/batches/<int:batch_id>', methods=['DELETE'])
def delete_batch(batch_id):
    """Delete a batch (and all related submissions)"""
    db = SessionLocal()
    try:
        batch = db.query(SubmissionBatch).filter(SubmissionBatch.id == batch_id).first()
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404

        db.delete(batch)
        db.commit()

        current_app.logger.info(f"Deleted batch {batch_id}")

        return jsonify({'message': 'Batch deleted successfully'}), 200
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error deleting batch {batch_id}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/accounts', methods=['GET'])
def get_accounts():
    """Get all RightFax accounts"""
    db = SessionLocal()
    try:
        accounts = db.query(RightFaxAccount).filter(
            RightFaxAccount.is_active == True
        ).all()

        return jsonify({
            'accounts': [account.to_dict() for account in accounts]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching accounts: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    db = SessionLocal()
    try:
        # Total batches
        total_batches = db.query(func.count(SubmissionBatch.id)).scalar()

        # Total submissions
        total_submissions = db.query(func.count(FaxSubmission.id)).scalar()

        # Total completions
        total_completions = db.query(func.count(FaxCompletion.id)).scalar()

        # Success rate
        successful = db.query(func.count(FaxCompletion.id)).filter(
            FaxCompletion.success == True
        ).scalar()
        success_rate = (successful / total_completions * 100) if total_completions > 0 else 0

        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_batches = db.query(func.count(SubmissionBatch.id)).filter(
            SubmissionBatch.created_at >= yesterday
        ).scalar()

        return jsonify({
            'total_batches': total_batches,
            'total_submissions': total_submissions,
            'total_completions': total_completions,
            'success_rate': round(success_rate, 2),
            'recent_batches_24h': recent_batches
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/completions', methods=['GET'])
def get_completions():
    """Get fax completions with filtering"""
    db = SessionLocal()
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        success = request.args.get('success')
        hours = request.args.get('hours', type=int)

        query = db.query(FaxCompletion).order_by(desc(FaxCompletion.completed_at))

        if success is not None:
            query = query.filter(FaxCompletion.success == (success.lower() == 'true'))

        if hours:
            since = datetime.utcnow() - timedelta(hours=hours)
            query = query.filter(FaxCompletion.completed_at >= since)

        total = query.count()
        completions = query.limit(limit).offset(offset).all()

        return jsonify({
            'completions': [c.to_dict() for c in completions],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching completions: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/celery/status', methods=['GET'])
def celery_status():
    """Check Celery worker status"""
    try:
        from app.celery_app import celery

        # Inspect active workers
        inspect = celery.control.inspect()

        # Get stats with timeout
        stats = inspect.stats()
        active = inspect.active()
        registered = inspect.registered()

        if not stats:
            return jsonify({
                'status': 'disconnected',
                'message': 'No Celery workers are running',
                'workers': []
            }), 503

        workers_info = []
        for worker_name, worker_stats in stats.items():
            workers_info.append({
                'name': worker_name,
                'status': 'online',
                'pool': worker_stats.get('pool', {}).get('implementation', 'unknown'),
                'active_tasks': len(active.get(worker_name, [])) if active else 0,
                'registered_tasks': len(registered.get(worker_name, [])) if registered else 0
            })

        return jsonify({
            'status': 'connected',
            'workers': workers_info,
            'worker_count': len(workers_info)
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error checking Celery status: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@bp.route('/database/reset', methods=['POST'])
def reset_database():
    """
    Delete all data from the database (REQ-PARSE-011)
    WARNING: This will delete ALL data!
    """
    db = SessionLocal()
    try:
        # Require confirmation
        data = request.get_json() or {}
        if data.get('confirm') != 'DELETE_ALL_DATA':
            return jsonify({
                'error': 'Confirmation required. Send {"confirm": "DELETE_ALL_DATA"}'
            }), 400

        # Delete all records (in order to respect foreign keys)
        db.query(FaxCompletion).delete()
        db.query(FaxSubmission).delete()
        db.query(SubmissionBatch).delete()
        db.commit()

        current_app.logger.warning("Database reset - all data deleted!")

        return jsonify({
            'message': 'All data has been deleted successfully'
        }), 200

    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error resetting database: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

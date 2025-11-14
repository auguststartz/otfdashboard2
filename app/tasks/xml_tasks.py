"""
Celery tasks for XML processing
"""
import logging
from app.celery_app import celery
from app.services.xml_parser import XMLParser
from app.database import SessionLocal

logger = logging.getLogger(__name__)


@celery.task(name='process_xml_file')
def process_xml_file(xml_filepath):
    """
    Process a single XML completion file
    """
    db = SessionLocal()
    try:
        parser = XMLParser(db)
        parser.process_xml_file(xml_filepath)
        logger.info(f"Processed XML file: {xml_filepath}")
    except Exception as e:
        logger.error(f"Error processing XML file {xml_filepath}: {e}")
    finally:
        db.close()


@celery.task(name='cleanup_old_archives')
def cleanup_old_archives():
    """
    Clean up old archived XML files based on retention policy
    """
    try:
        from app.services.xml_parser import XMLParser
        XMLParser.cleanup_old_archives()
        logger.info("Cleaned up old XML archives")
    except Exception as e:
        logger.error(f"Error cleaning up archives: {e}")

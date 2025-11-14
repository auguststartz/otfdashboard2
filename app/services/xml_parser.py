"""
XML Parser for RightFax Completion Files
Parses XML files written by RightFax and stores data in database
"""
import os
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from lxml import etree
from app.config import Config
from app.models import FaxCompletion, FaxSubmission

logger = logging.getLogger(__name__)


class XMLParser:
    """
    Parses RightFax XML completion files
    """

    def __init__(self, db_session):
        """
        Initialize XML Parser

        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
        self.xml_directory = Config.RIGHTFAX_XML_DIRECTORY
        self.archive_directory = Config.XML_ARCHIVE_FOLDER

        # Ensure directories exist
        Path(self.archive_directory).mkdir(parents=True, exist_ok=True)

    def process_xml_file(self, xml_filepath):
        """
        Process a single XML completion file

        Args:
            xml_filepath: Path to XML file

        Returns:
            bool: True if processed successfully
        """
        try:
            logger.info(f"Processing XML file: {xml_filepath}")

            # Parse XML
            tree = etree.parse(xml_filepath)
            root = tree.getroot()

            # Extract data from XML
            completion_data = self._extract_completion_data(root, xml_filepath)

            if not completion_data:
                logger.warning(f"No data extracted from {xml_filepath}")
                self._move_to_error(xml_filepath)
                return False

            # Check for duplicate
            existing = self.db.query(FaxCompletion).filter(
                FaxCompletion.rightfax_job_id == completion_data['rightfax_job_id']
            ).first()

            if existing:
                logger.info(f"Duplicate job ID {completion_data['rightfax_job_id']}, skipping")
                self._archive_file(xml_filepath)
                return True

            # Try to find corresponding submission
            submission = self.db.query(FaxSubmission).filter(
                FaxSubmission.rightfax_job_id == completion_data['rightfax_job_id']
            ).first()

            if submission:
                completion_data['submission_id'] = submission.id
                logger.debug(f"Linked completion to submission {submission.id}")

            # Create completion record
            completion = FaxCompletion(**completion_data)
            self.db.add(completion)
            self.db.commit()

            logger.info(f"Stored completion for job {completion_data['rightfax_job_id']}")

            # Archive the XML file
            self._archive_file(xml_filepath)

            return True

        except etree.XMLSyntaxError as e:
            logger.error(f"XML parsing error in {xml_filepath}: {e}")
            self._move_to_error(xml_filepath)
            return False

        except Exception as e:
            logger.error(f"Error processing XML file {xml_filepath}: {e}")
            self.db.rollback()
            return False

    def _extract_completion_data(self, root, xml_filepath):
        """
        Extract completion data from XML tree

        Args:
            root: XML root element
            xml_filepath: Path to XML file

        Returns:
            dict: Completion data for database
        """
        try:
            # Read raw XML for storage
            with open(xml_filepath, 'r', encoding='ISO-8859-1') as f:
                raw_xml = f.read()

            # Find all IndexField elements
            index_fields = {}
            for field in root.findall('.//IndexField'):
                name = field.get('Name')
                value = field.get('Value')
                if name and value:
                    index_fields[name] = value

            # Extract required fields
            unique_id = index_fields.get('UniqueID')
            if not unique_id:
                logger.error("No UniqueID found in XML")
                return None

            # Parse timestamps
            completed_at = self._parse_timestamp(
                index_fields.get('Fax Completion Time')
            )
            submitted_at = self._parse_timestamp(
                index_fields.get('Fax Create Time')
            )
            job_create_time = self._parse_timestamp(
                index_fields.get('Job Create Time')
            )

            if not completed_at:
                logger.error("No completion time found in XML")
                return None

            # Parse duration
            duration_str = index_fields.get('Send Duration') or index_fields.get('Elapsed Time')
            duration_seconds = self._parse_duration(duration_str)

            # Determine success/failure
            disposition = int(index_fields.get('Disposition', 0))
            term_stat = int(index_fields.get('TermStat', 0))
            success = (disposition == 0 and term_stat in [0, 32])  # Common success codes

            # Extract page counts
            good_pages = int(index_fields.get('Good Page Count', 0))
            bad_pages = int(index_fields.get('Bad Page Count', 0))

            # Build completion data
            completion_data = {
                'rightfax_job_id': unique_id,
                'completed_at': completed_at,
                'submitted_at': submitted_at,
                'duration_seconds': duration_seconds,
                'success': success,
                'recipient_phone': index_fields.get('To Fax Number'),
                'pages_transmitted': good_pages,
                'account_name': index_fields.get('User ID'),
                'xml_filename': os.path.basename(xml_filepath),
                'raw_xml': raw_xml,
                'fax_handle': index_fields.get('Fax Handle'),
                'fax_channel': index_fields.get('Fax Channel'),
                'job_create_time': job_create_time,
                'fax_create_time': submitted_at,
                'fax_server': index_fields.get('Fax Server'),
                'job_type': index_fields.get('Type'),
                'disposition': disposition,
                'term_stat': term_stat,
                'good_page_count': good_pages,
                'bad_page_count': bad_pages
            }

            # Add error information if failed
            if not success:
                completion_data['error_code'] = str(term_stat)
                completion_data['error_description'] = f"Disposition: {disposition}, TermStat: {term_stat}"

            return completion_data

        except Exception as e:
            logger.error(f"Error extracting data from XML: {e}")
            return None

    def _parse_timestamp(self, timestamp_str):
        """
        Parse timestamp string from XML

        Args:
            timestamp_str: Timestamp string (e.g., "11/14/2025 3:56:57 AM")

        Returns:
            datetime: Parsed datetime or None
        """
        if not timestamp_str:
            return None

        try:
            # Try common formats
            formats = [
                '%m/%d/%Y %I:%M:%S %p',  # 11/14/2025 3:56:57 AM
                '%m/%d/%Y %H:%M:%S',     # 11/14/2025 15:56:57
                '%Y-%m-%d %H:%M:%S',     # 2025-11-14 15:56:57
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue

            logger.warning(f"Could not parse timestamp: {timestamp_str}")
            return None

        except Exception as e:
            logger.error(f"Error parsing timestamp {timestamp_str}: {e}")
            return None

    def _parse_duration(self, duration_str):
        """
        Parse duration string to seconds

        Args:
            duration_str: Duration string (e.g., "00:00:37")

        Returns:
            int: Duration in seconds
        """
        if not duration_str:
            return None

        try:
            parts = duration_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            return None
        except Exception as e:
            logger.error(f"Error parsing duration {duration_str}: {e}")
            return None

    def _archive_file(self, xml_filepath):
        """
        Move processed XML file to archive directory

        Args:
            xml_filepath: Path to XML file
        """
        try:
            # Create date-based subdirectory
            today = datetime.now().strftime('%Y-%m-%d')
            archive_dir = os.path.join(self.archive_directory, today)
            Path(archive_dir).mkdir(parents=True, exist_ok=True)

            # Move file
            filename = os.path.basename(xml_filepath)
            archive_path = os.path.join(archive_dir, filename)

            shutil.move(xml_filepath, archive_path)
            logger.debug(f"Archived XML file to {archive_path}")

        except Exception as e:
            logger.error(f"Error archiving file {xml_filepath}: {e}")

    def _move_to_error(self, xml_filepath):
        """
        Move malformed XML file to error directory

        Args:
            xml_filepath: Path to XML file
        """
        try:
            error_dir = os.path.join(self.archive_directory, 'errors')
            Path(error_dir).mkdir(parents=True, exist_ok=True)

            filename = os.path.basename(xml_filepath)
            error_path = os.path.join(error_dir, filename)

            shutil.move(xml_filepath, error_path)
            logger.warning(f"Moved malformed XML to {error_path}")

        except Exception as e:
            logger.error(f"Error moving file to error directory: {e}")

    @staticmethod
    def cleanup_old_archives():
        """
        Clean up old archived XML files based on retention policy
        """
        try:
            archive_dir = Config.XML_ARCHIVE_FOLDER
            retention_days = Config.XML_RETENTION_DAYS
            cutoff_date = datetime.now() - timedelta(days=retention_days)

            logger.info(f"Cleaning up archives older than {retention_days} days")

            deleted_count = 0
            for root, dirs, files in os.walk(archive_dir):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))

                    if file_mtime < cutoff_date:
                        os.remove(filepath)
                        deleted_count += 1

            logger.info(f"Deleted {deleted_count} old archive files")

        except Exception as e:
            logger.error(f"Error cleaning up archives: {e}")

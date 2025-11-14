"""
XML File Watcher Service
Monitors directory for new XML files from RightFax and triggers processing
"""
import os
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.config import Config
from app.database import SessionLocal
from app.services.xml_parser import XMLParser

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XMLFileHandler(FileSystemEventHandler):
    """
    Handler for XML file system events
    """

    def __init__(self):
        super().__init__()
        self.processing = set()  # Track files currently being processed

    def on_created(self, event):
        """
        Handle file creation event

        Args:
            event: File system event
        """
        if event.is_directory:
            return

        # Only process XML files
        if not event.src_path.lower().endswith('.xml'):
            return

        # Avoid processing the same file multiple times
        if event.src_path in self.processing:
            return

        logger.info(f"New XML file detected: {event.src_path}")

        # Wait a moment to ensure file is completely written
        time.sleep(1)

        # Process the file
        self._process_file(event.src_path)

    def _process_file(self, filepath):
        """
        Process an XML file

        Args:
            filepath: Path to XML file
        """
        self.processing.add(filepath)

        try:
            # Check if file still exists and is readable
            if not os.path.exists(filepath):
                logger.warning(f"File disappeared: {filepath}")
                return

            # Wait until file is no longer being written
            if not self._wait_for_file_ready(filepath):
                logger.warning(f"File not ready: {filepath}")
                return

            # Process with XMLParser
            db = SessionLocal()
            try:
                parser = XMLParser(db)
                parser.process_xml_file(filepath)
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error processing file {filepath}: {e}")

        finally:
            self.processing.discard(filepath)

    def _wait_for_file_ready(self, filepath, timeout=30, check_interval=0.5):
        """
        Wait for file to be completely written

        Args:
            filepath: Path to file
            timeout: Maximum time to wait (seconds)
            check_interval: Time between checks (seconds)

        Returns:
            bool: True if file is ready, False if timeout
        """
        start_time = time.time()
        last_size = -1

        while time.time() - start_time < timeout:
            try:
                current_size = os.path.getsize(filepath)

                if current_size == last_size and current_size > 0:
                    # File size hasn't changed, assume it's complete
                    return True

                last_size = current_size
                time.sleep(check_interval)

            except OSError:
                # File may not be accessible yet
                time.sleep(check_interval)

        logger.warning(f"Timeout waiting for file to be ready: {filepath}")
        return False


def start_xml_watcher():
    """
    Start the XML file watcher service
    """
    xml_directory = Config.RIGHTFAX_XML_DIRECTORY

    # Ensure directory exists
    Path(xml_directory).mkdir(parents=True, exist_ok=True)

    logger.info(f"Starting XML file watcher for directory: {xml_directory}")

    # Create observer and handler
    event_handler = XMLFileHandler()
    observer = Observer()
    observer.schedule(event_handler, xml_directory, recursive=False)

    # Start watching
    observer.start()

    try:
        logger.info("XML file watcher started successfully")

        # Keep the watcher running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Stopping XML file watcher...")
        observer.stop()

    observer.join()
    logger.info("XML file watcher stopped")


if __name__ == '__main__':
    # Run the watcher
    start_xml_watcher()

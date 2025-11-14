"""
FCL (Fax Command Language) File Generator
Generates FCL files for RightFax submission
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from app.config import Config

logger = logging.getLogger(__name__)


class FCLGenerator:
    """
    Generates FCL files for RightFax fax submissions
    """

    def __init__(self, fcl_directory=None):
        """
        Initialize FCL Generator

        Args:
            fcl_directory: Directory to write FCL files (defaults to config)
        """
        self.fcl_directory = fcl_directory or Config.RIGHTFAX_FCL_DIRECTORY
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure FCL directory exists"""
        try:
            Path(self.fcl_directory).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating FCL directory {self.fcl_directory}: {e}")
            raise

    def generate_fcl(self, recipient_phone, account_name, attachment_filename=None,
                    recipient_name=None, subject=None, priority='NORMAL',
                    coverpage=None):
        """
        Generate an FCL file for fax submission

        Args:
            recipient_phone: Recipient fax number (required)
            account_name: RightFax account/user ID (required)
            attachment_filename: Path to attachment file
            recipient_name: Recipient name (optional)
            subject: Fax subject (optional)
            priority: Priority level (LOW, NORMAL, HIGH)
            coverpage: Cover page template name (optional)

        Returns:
            str: Filename of generated FCL file

        Raises:
            ValueError: If required parameters are missing
            IOError: If FCL file cannot be written
        """
        # Validate required parameters
        if not recipient_phone:
            raise ValueError("recipient_phone is required")
        if not account_name:
            raise ValueError("account_name is required")

        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        sequence = os.getpid() % 10000  # Use process ID for uniqueness
        fcl_filename = f"fax_{timestamp}_{sequence:04d}.fcl"
        fcl_path = os.path.join(self.fcl_directory, fcl_filename)

        # Build FCL content
        fcl_content = self._build_fcl_content(
            recipient_phone=recipient_phone,
            recipient_name=recipient_name,
            account_name=account_name,
            attachment_filename=attachment_filename,
            subject=subject,
            priority=priority,
            coverpage=coverpage
        )

        # Write FCL file atomically
        try:
            # Write to temporary file first
            temp_path = fcl_path + '.tmp'
            with open(temp_path, 'w') as f:
                f.write(fcl_content)

            # Rename to final name (atomic operation)
            os.rename(temp_path, fcl_path)

            logger.info(f"Generated FCL file: {fcl_filename}")
            logger.debug(f"FCL content:\n{fcl_content}")

            return fcl_filename

        except Exception as e:
            logger.error(f"Error writing FCL file {fcl_filename}: {e}")
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise IOError(f"Failed to write FCL file: {e}")

    def _build_fcl_content(self, recipient_phone, account_name, attachment_filename=None,
                          recipient_name=None, subject=None, priority='NORMAL',
                          coverpage=None):
        """
        Build FCL file content according to RightFax FCL specification

        FCL Format (from PRD example):
        {{begin}}

        {{fax 904-202-0999}}
        {{attach C:\\CustomFolder\\Attachments\\document.pdf}}

        {{winsecid AUGUST}}

        {{end}}
        """
        lines = []

        # Begin block
        lines.append("{{begin}}")
        lines.append("")

        # Recipient fax number
        lines.append(f"{{{{fax {recipient_phone}}}}}")

        # Attachment file (if provided)
        if attachment_filename:
            # Convert path for Windows if needed
            attachment_path = attachment_filename.replace('/', '\\\\')
            lines.append(f"{{{{attach {attachment_path}}}}}")

        lines.append("")

        # Account/User ID (winsecid)
        lines.append(f"{{{{winsecid {account_name}}}}}")

        lines.append("")

        # Additional optional parameters
        if recipient_name:
            lines.append(f"{{{{to-name {recipient_name}}}}}")

        if subject:
            lines.append(f"{{{{subject {subject}}}}}")

        if coverpage:
            lines.append(f"{{{{coverpage {coverpage}}}}}")

        if priority and priority != 'NORMAL':
            lines.append(f"{{{{priority {priority}}}}}")

        # End block
        lines.append("{{end}}")

        return '\n'.join(lines)

    def validate_attachment(self, attachment_path):
        """
        Validate that attachment file exists and is accessible

        Args:
            attachment_path: Path to attachment file

        Returns:
            bool: True if valid, False otherwise
        """
        if not attachment_path:
            return True  # Attachment is optional

        if not os.path.exists(attachment_path):
            logger.error(f"Attachment file not found: {attachment_path}")
            return False

        if not os.path.isfile(attachment_path):
            logger.error(f"Attachment path is not a file: {attachment_path}")
            return False

        return True

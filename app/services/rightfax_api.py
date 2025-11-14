"""
RightFax REST API Client
Handles communication with RightFax REST API for fax submission
"""
import requests
import logging
import base64
from typing import Dict, Optional
from app.config import Config

logger = logging.getLogger(__name__)


class RightFaxAPIClient:
    """
    Client for RightFax REST API
    """

    def __init__(self, api_url=None, username=None, password=None):
        """
        Initialize API client

        Args:
            api_url: RightFax API base URL (defaults to config)
            username: RightFax API username (defaults to config)
            password: RightFax API password (defaults to config)
        """
        self.api_url = (api_url or Config.RIGHTFAX_API_URL).rstrip('/')
        self.username = username or Config.RIGHTFAX_USERNAME
        self.password = password or Config.RIGHTFAX_PASSWORD
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

        # Set up Basic Authentication if credentials provided
        if self.username and self.password:
            self.session.auth = (self.username, self.password)

        if not self.api_url:
            logger.warning("RightFax API URL not configured")

        if not self.username or not self.password:
            logger.warning("RightFax API credentials not configured")

    def submit_fax(self, recipient_phone: str, account_name: str,
                  attachment_path: Optional[str] = None,
                  recipient_name: Optional[str] = None,
                  subject: Optional[str] = None,
                  priority: str = 'NORMAL',
                  coverpage: Optional[str] = None) -> Dict:
        """
        Submit a fax via RightFax REST API

        Args:
            recipient_phone: Recipient fax number
            account_name: RightFax account name
            attachment_path: Path to attachment file
            recipient_name: Recipient name
            subject: Fax subject
            priority: Priority level (LOW, NORMAL, HIGH)
            coverpage: Cover page template name

        Returns:
            dict: API response with job_id and status_code

        Raises:
            ValueError: If required parameters missing
            requests.RequestException: If API call fails
        """
        if not recipient_phone:
            raise ValueError("recipient_phone is required")
        if not account_name:
            raise ValueError("account_name is required")

        # Build request payload
        payload = {
            "recipient": {
                "number": recipient_phone
            },
            "sender": {
                "account": account_name
            },
            "options": {
                "priority": priority
            }
        }

        # Add optional fields
        if recipient_name:
            payload["recipient"]["name"] = recipient_name

        if subject:
            payload["subject"] = subject

        if coverpage:
            payload["options"]["coverPage"] = coverpage

        # Encode attachment if provided
        if attachment_path:
            try:
                with open(attachment_path, 'rb') as f:
                    file_content = f.read()
                    encoded_content = base64.b64encode(file_content).decode('utf-8')

                payload["document"] = {
                    "base64": encoded_content,
                    "filename": attachment_path.split('/')[-1],
                    "contentType": self._get_content_type(attachment_path)
                }
            except Exception as e:
                logger.error(f"Error encoding attachment {attachment_path}: {e}")
                raise

        # Make API request
        try:
            endpoint = f"{self.api_url}/faxes"

            logger.info(f"Submitting fax to {recipient_phone} via API")
            logger.debug(f"API endpoint: {endpoint}")

            # Session already has auth configured in __init__
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=30
            )

            # Check response
            if response.status_code in [200, 201]:
                response_data = response.json()
                job_id = response_data.get('jobId') or response_data.get('id')

                logger.info(f"Fax submitted successfully: Job ID {job_id}")

                return {
                    'success': True,
                    'job_id': job_id,
                    'status_code': response.status_code,
                    'response': response_data
                }
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'job_id': None,
                    'status_code': response.status_code,
                    'error': response.text
                }

        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def get_fax_status(self, job_id: str) -> Dict:
        """
        Get status of a fax job

        Args:
            job_id: RightFax job ID

        Returns:
            dict: Job status information
        """
        try:
            endpoint = f"{self.api_url}/faxes/{job_id}"

            # Session already has auth configured in __init__
            response = self.session.get(endpoint, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get job status: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            return None

    def _get_content_type(self, filename: str) -> str:
        """
        Determine content type from filename

        Args:
            filename: File name

        Returns:
            str: MIME content type
        """
        ext = filename.lower().split('.')[-1]
        content_types = {
            'pdf': 'application/pdf',
            'tif': 'image/tiff',
            'tiff': 'image/tiff',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain'
        }
        return content_types.get(ext, 'application/octet-stream')

    def test_connection(self) -> bool:
        """
        Test API connection

        Returns:
            bool: True if connection successful
        """
        try:
            # Try to ping API endpoint or just test the base URL
            endpoint = f"{self.api_url}/health"

            # Session already has auth configured in __init__
            response = self.session.get(endpoint, timeout=5)
            return response.status_code in [200, 401]  # 401 means auth issue but API is reachable

        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False

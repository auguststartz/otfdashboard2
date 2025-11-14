"""
Configuration management for RightFax Testing Platform
"""
import os
from pathlib import Path


class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # Database
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'rightfax_testing')
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'changeme')

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = FLASK_ENV == 'development'

    # Redis/Celery
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # RightFax Configuration
    RIGHTFAX_API_URL = os.getenv('RIGHTFAX_API_URL', '')
    RIGHTFAX_USERNAME = os.getenv('RIGHTFAX_USERNAME', '')
    RIGHTFAX_PASSWORD = os.getenv('RIGHTFAX_PASSWORD', '')
    RIGHTFAX_FCL_DIRECTORY = os.getenv('RIGHTFAX_FCL_DIRECTORY', '/mnt/rightfax/fcl')
    RIGHTFAX_XML_DIRECTORY = os.getenv('RIGHTFAX_XML_DIRECTORY', '/mnt/rightfax/xml')

    # Application Directories
    BASE_DIR = Path(__file__).parent.parent
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    XML_ARCHIVE_FOLDER = os.getenv('XML_ARCHIVE_FOLDER', str(BASE_DIR / 'xml_archive'))
    LOG_FOLDER = os.getenv('LOG_FOLDER', str(BASE_DIR / 'logs'))

    # File Upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'tiff', 'tif', 'doc', 'docx'}

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # XML Processing
    XML_RETENTION_DAYS = int(os.getenv('XML_RETENTION_DAYS', '90'))

    # Batch Submission Limits
    MAX_BATCH_SIZE = int(os.getenv('MAX_BATCH_SIZE', '100000'))
    MAX_INTERVAL_SECONDS = int(os.getenv('MAX_INTERVAL_SECONDS', '300'))

    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create necessary directories
        for directory in [Config.UPLOAD_FOLDER, Config.XML_ARCHIVE_FOLDER, Config.LOG_FOLDER]:
            Path(directory).mkdir(parents=True, exist_ok=True)

        # Validate critical configuration
        if not Config.POSTGRES_PASSWORD or Config.POSTGRES_PASSWORD == 'changeme':
            if Config.FLASK_ENV == 'production':
                raise ValueError("POSTGRES_PASSWORD must be set in production")

        # Check RightFax directories exist (in development, create them)
        if Config.FLASK_ENV == 'development':
            Path(Config.RIGHTFAX_FCL_DIRECTORY).mkdir(parents=True, exist_ok=True)
            Path(Config.RIGHTFAX_XML_DIRECTORY).mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

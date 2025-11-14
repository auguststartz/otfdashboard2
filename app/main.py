"""
Main Flask Application for RightFax Testing & Monitoring Platform
"""
import logging
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from app.config import config, Config
from app.database import SessionLocal
import os


def create_app(config_name=None):
    """
    Application factory pattern
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize configuration
    Config.init_app(app)

    # Setup CORS
    CORS(app)

    # Setup logging
    setup_logging(app)

    # Register blueprints
    from app.routes import api, web
    app.register_blueprint(api.bp)
    app.register_blueprint(web.bp)

    # Database session teardown
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        SessionLocal.remove()

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal error: {error}")
        SessionLocal.remove()
        return jsonify({'error': 'Internal server error'}), 500

    # Health check endpoint
    @app.route('/health')
    def health():
        """Health check endpoint for monitoring"""
        try:
            # Check database connection
            db = SessionLocal()
            db.execute('SELECT 1')
            db.close()
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'version': '1.0.0'
            }), 200
        except Exception as e:
            app.logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'error': str(e)
            }), 500

    app.logger.info(f"Application started in {config_name} mode")

    return app


def setup_logging(app):
    """
    Configure application logging
    """
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper())

    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # File handler
    log_file = os.path.join(app.config['LOG_FOLDER'], 'app.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Configure app logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)

    # Configure werkzeug logger
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)


# Create the application instance
app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

"""
Web UI Routes for RightFax Testing Platform
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os

bp = Blueprint('web', __name__)


@bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@bp.route('/batches')
def batches():
    """Batch management page"""
    return render_template('batches.html')


@bp.route('/submit')
def submit():
    """Fax submission form page"""
    return render_template('submit.html')


@bp.route('/monitoring')
def monitoring():
    """Redirect to Grafana dashboard"""
    return redirect('/grafana')


@bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload for attachments"""
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400

    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    if file:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)

        current_app.logger.info(f"File uploaded: {filename}")

        return {
            'message': 'File uploaded successfully',
            'filename': filename
        }, 200

"""
Control routes and other device endpoints
"""
import os
from flask import Blueprint, send_from_directory


control_bp = Blueprint('control', __name__)


@control_bp.route("/")
def index():
    """Serve the main UI (index.html)"""
    # Get the absolute path to the Frontend directory
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Frontend')
    return send_from_directory(frontend_dir, "index.html")

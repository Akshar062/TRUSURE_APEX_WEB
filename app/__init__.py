"""
Flask application factory and configuration
"""
import threading
from flask import Flask
from picamera2 import Picamera2


# Global variables for camera and thread lock
picam2 = None
lock = threading.Lock()


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder="../Frontend", static_url_path="")
    
    # Initialize camera
    init_camera()
    
    # Register blueprints
    from .camera_routes import camera_bp
    from .control_routes import control_bp
    
    app.register_blueprint(camera_bp)
    app.register_blueprint(control_bp)
    
    return app


def init_camera():
    global picam2
    if picam2 is not None:
        return  # Already initialized
    
    try:
        picam2 = Picamera2()
        sensorSize = picam2.sensor_resolution
        preview_config = picam2.create_preview_configuration(
            main={"size": (sensorSize[0] // 3, sensorSize[1] // 3)},
            controls={
                "AfMode": 2,
            }
        )
        picam2.configure(preview_config)
        picam2.start()
        print("Camera initialized successfully")
    except Exception as e:
        print(f"Failed to initialize camera: {e}")
        picam2 = None



def get_camera():
    """Get the camera instance"""
    return picam2


def get_lock():
    """Get the thread lock"""
    return lock

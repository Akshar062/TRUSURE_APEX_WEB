"""
Utility functions and helpers
"""
import threading
from picamera2 import Picamera2


def setup_camera():
    """Setup and configure the camera with default settings"""
    picam2 = Picamera2()
    sensorSize = picam2.sensor_resolution
    preview_config = picam2.create_preview_configuration(
        main={"size": (sensorSize[0] // 4, sensorSize[1] // 4)},
    )
    picam2.configure(preview_config)
    return picam2


def create_thread_lock():
    """Create a thread lock for camera operations"""
    return threading.Lock()


def validate_camera_settings(width, height, fps):
    """Validate camera settings parameters"""
    try:
        width = int(width)
        height = int(height)
        fps = int(fps)
        
        # Basic validation
        if width <= 0 or height <= 0 or fps <= 0:
            return False, "Width, height, and fps must be positive integers"
        
        if fps > 60:
            return False, "FPS cannot exceed 60"
            
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid parameter types"


def validate_focus_settings(mode, position):
    """Validate focus settings parameters"""
    if mode not in ["auto", "manual"]:
        return False, "Mode must be 'auto' or 'manual'"
    
    try:
        position = float(position)
        # Accept both 0-1 range (direct lens position) and 0-100 range (slider value)
        if 0.0 <= position <= 1.0:
            # Already in correct range
            return True, None
        elif 0.0 <= position <= 100.0:
            # Convert from slider range (0-100) to lens position range (0-1)
            return True, None
        else:
            return False, "Position must be between 0.0 and 100.0"
    except (ValueError, TypeError):
        return False, "Position must be a valid number"

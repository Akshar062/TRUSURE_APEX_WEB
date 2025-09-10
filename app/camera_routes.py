"""
Camera-related routes and streaming functionality
"""
import io
import time
from flask import Blueprint, Response, request, jsonify
from . import get_camera, get_lock
from .utils import validate_camera_settings, validate_focus_settings


camera_bp = Blueprint('camera', __name__)


@camera_bp.route("/stream")
def stream():
    """MJPEG Preview Stream"""
    def generate():
        picam2 = get_camera()
        lock = get_lock()
        
        if picam2 is None:
            # Return a simple error frame
            error_frame = b"Camera not available"
            while True:
                yield (b"--frame\r\n"
                       b"Content-Type: text/plain\r\n\r\n" + error_frame + b"\r\n")
                time.sleep(1)
        
        while True:
            with lock:
                try:
                    buf = io.BytesIO()
                    picam2.capture_file(buf, format="jpeg")
                    buf.seek(0)
                    frame = buf.getvalue()
                except Exception as e:
                    # Return error frame if capture fails
                    error_frame = f"Camera error: {str(e)}".encode()
                    yield (b"--frame\r\n"
                           b"Content-Type: text/plain\r\n\r\n" + error_frame + b"\r\n")
                    time.sleep(1)
                    continue
                    
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(0.03)  # ~30 fps
    
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@camera_bp.route("/api/camera/get_control_range", methods=["POST"])
def get_control_range():
    """Get camera controls range"""
    picam2 = get_camera()
    lock = get_lock()
    
    if picam2 is None:
        return jsonify({"success": False, "message": "Camera not available"}), 503
    
    data = request.json or {}
    control_name = data.get("control_name", "")
    if not control_name:
        return jsonify({"success": False, "message": "No control name provided"}), 400

    with lock:
        try:
            controls = picam2.camera_controls
            if control_name not in controls:
                return jsonify({"success": False, "message": f"Control '{control_name}' not found"}), 404

            min_val, max_val, default_val = controls[control_name]

            return jsonify({
                "success": True,
                "min": min_val,
                "max": max_val,
                "current": default_val
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

@camera_bp.route("/api/camera/trigger_af", methods=["POST"])
def trigger_af():
    """Trigger auto focus"""
    picam2 = get_camera()
    lock = get_lock()
    
    if picam2 is None:
        return jsonify({"success": False, "message": "Camera not available"}), 503

    with lock:
        try:
            # Step 1: Switch to auto focus mode
            picam2.set_controls({"AfMode": 1})
            time.sleep(0.05)  # tiny delay to ensure camera registers mode

            # Step 2: Trigger autofocus
            picam2.set_controls({"AfTrigger": 0})
            
            return jsonify({"success": True, "message": "Auto focus triggered"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500


@camera_bp.route("/api/camera/set_focus", methods=["POST"])
def set_focus():
    """Set camera focus"""
    picam2 = get_camera()
    lock = get_lock()
    
    if picam2 is None:
        return jsonify({"success": False, "message": "Camera not available"}), 503
    
    data = request.json or {}
    mode = data.get("mode", "auto")       # "auto" or "manual"
    position = data.get("position", 0.0)  # float between 0.0 and 100.0 (slider) or 0.0-1.0 (direct)

    # Validate focus settings
    is_valid, error_msg = validate_focus_settings(mode, position)
    if not is_valid:
        return jsonify({"success": False, "message": error_msg}), 400

    position_float = float(position)

    with lock:
        try:
            picam2.set_controls({"AfMode": 0})
            if mode == "manual":
                picam2.set_controls({"LensPosition": position_float})
            return jsonify({"success": True, "message": f"Focus set to {mode} / {position_float:.3f}"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
        

# gain controls
@camera_bp.route("/api/camera/set_gain", methods=["POST"])
def set_gain():
    """Set camera gain"""
    picam2 = get_camera()
    lock = get_lock()
    
    if picam2 is None:
        return jsonify({"success": False, "message": "Camera not available"}), 503
    
    data = request.json or {}
    gain = data.get("gain", 1.0)  # float between 1.0 and 64.0

    try:
        gain_float = float(gain)
        if not (1.0 <= gain_float <= 64.0):
            raise ValueError("Gain must be between 1.0 and 64.0")
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400

    with lock:
        try:
            picam2.set_controls({"AnalogueGain": gain_float})
            return jsonify({"success": True, "message": f"Gain set to {gain_float:.2f}"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500


@camera_bp.route("/api/camera/start", methods=["POST"])
def start_camera():
    """Start the camera"""
    picam2 = get_camera()
    lock = get_lock()
    
    if picam2 is None:
        return jsonify({"success": False, "message": "Camera not available"}), 503
    
    with lock:
        try:
            if not picam2.started:
                picam2.start()
            return jsonify({"success": True, "message": "Camera started"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500


@camera_bp.route("/api/camera/stop", methods=["POST"])
def stop_camera():
    """Stop the camera"""
    picam2 = get_camera()
    lock = get_lock()
    
    if picam2 is None:
        return jsonify({"success": False, "message": "Camera not available"}), 503
    
    with lock:
        try:
            if picam2.started:
                picam2.stop()
            return jsonify({"success": True, "message": "Camera stopped"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500


@camera_bp.route("/api/camera/set", methods=["POST"])
def set_camera():
    """Set camera configuration"""
    picam2 = get_camera()
    lock = get_lock()
    
    if picam2 is None:
        return jsonify({"success": False, "message": "Camera not available"}), 503
    
    data = request.json or {}
    width = data.get("width", 640)
    height = data.get("height", 480)
    fps = data.get("fps", 30)

    # Validate camera settings
    is_valid, error_msg = validate_camera_settings(width, height, fps)
    if not is_valid:
        return jsonify({"success": False, "message": error_msg}), 400

    width = int(width)
    height = int(height)
    fps = int(fps)

    with lock:
        try:
            config = picam2.create_video_configuration(
                main={"size": (width, height)},
                controls={"FrameRate": fps},
            )
            picam2.stop()
            picam2.configure(config)
            picam2.start()
            return jsonify({"success": True, "message": "Camera settings updated"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500


@camera_bp.route("/api/camera/status")
def status():
    """Get camera status"""
    picam2 = get_camera()
    
    if picam2 is None:
        return jsonify({
            "started": False,
            "resolution": None,
            "available": False,
            "message": "Camera not available"
        })
    
    try:
        return jsonify({
            "started": picam2.started,
            "resolution": picam2.camera_configuration()["main"]["size"],
            "available": True
        })
    except Exception as e:
        return jsonify({
            "started": False,
            "resolution": None,
            "available": False,
            "message": str(e)
        })

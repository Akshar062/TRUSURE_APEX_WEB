"""
Camera-related routes and streaming functionality (simplified)
"""
import io
import time
from flask import Blueprint, Response, request, jsonify
from functools import wraps
from . import get_camera, get_lock
from .utils import validate_camera_settings, validate_focus_settings


camera_bp = Blueprint("camera", __name__)


# ----------------------------
# Helpers
# ----------------------------
def with_camera(func):
    """Decorator to ensure camera and lock are available"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        picam2 = get_camera()
        if picam2 is None:
            return jsonify({"success": False, "message": "Camera not available"}), 503
        lock = get_lock()
        with lock:
            return func(picam2, *args, **kwargs)
    return wrapper


def error_response(msg, code=400):
    return jsonify({"success": False, "message": msg}), code


# ----------------------------
# Routes
# ----------------------------
@camera_bp.route("/stream")
def stream():
    """MJPEG Preview Stream"""
    def generate():
        picam2 = get_camera()
        lock = get_lock()

        if picam2 is None:
            while True:
                yield (b"--frame\r\nContent-Type: text/plain\r\n\r\nCamera not available\r\n")
                time.sleep(1)

        while True:
            with lock:
                try:
                    buf = io.BytesIO()
                    picam2.capture_file(buf, format="jpeg")
                    frame = buf.getvalue()
                except Exception as e:
                    yield (b"--frame\r\nContent-Type: text/plain\r\n\r\n"
                           + f"Camera error: {e}".encode() + b"\r\n")
                    time.sleep(1)
                    continue

            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(0.03)  # ~30 fps

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@camera_bp.route("/api/camera/get_control_range", methods=["POST"])
@with_camera
def get_control_range(picam2):
    data = request.json or {}
    control_name = data.get("control_name")
    if not control_name:
        return error_response("No control name provided")

    try:
        controls = picam2.camera_controls
        if control_name not in controls:
            return error_response(f"Control '{control_name}' not found", 404)

        min_val, max_val, default_val = controls[control_name]
        return jsonify({"success": True, "min": min_val, "max": max_val, "current": default_val})
    except Exception as e:
        return error_response(str(e), 500)


@camera_bp.route("/api/camera/trigger_af", methods=["POST"])
@with_camera
def trigger_af(picam2):
    try:
        picam2.set_controls({"AfMode": 1})
        time.sleep(0.05)
        picam2.set_controls({"AfTrigger": 0})
        return jsonify({"success": True, "message": "Auto focus triggered"})
    except Exception as e:
        return error_response(str(e), 500)


@camera_bp.route("/api/camera/set_focus", methods=["POST"])
@with_camera
def set_focus(picam2):
    data = request.json or {}
    mode = data.get("mode", "auto")
    position = data.get("position", 0.0)

    ok, err = validate_focus_settings(mode, position)
    if not ok:
        return error_response(err)

    try:
        picam2.set_controls({"AfMode": 0})
        if mode == "manual":
            picam2.set_controls({"LensPosition": float(position)})
        return jsonify({"success": True, "message": f"Focus set to {mode} / {float(position):.3f}"})
    except Exception as e:
        return error_response(str(e), 500)


@camera_bp.route("/api/camera/set_exposure", methods=["POST"])
@with_camera
def set_exposure(picam2):
    exposure = (request.json or {}).get("exposure", 10000)
    try:
        exposure = float(exposure)
        if not (1000 <= exposure <= 1_000_000):
            raise ValueError("Exposure must be between 1000 and 1000000 µs")
        picam2.set_controls({"AeEnable": False, "ExposureTime": exposure})
        return jsonify({"success": True, "message": f"Exposure set to {exposure:.2f} µs"})
    except Exception as e:
        return error_response(str(e), 400)


@camera_bp.route("/api/camera/set_gain", methods=["POST"])
@with_camera
def set_gain(picam2):
    gain = (request.json or {}).get("gain", 1.0)
    try:
        gain = float(gain)
        if not (1.0 <= gain <= 64.0):
            raise ValueError("Gain must be between 1.0 and 64.0")
        picam2.set_controls({"AeEnable": False, "AnalogueGain": gain})
        return jsonify({"success": True, "message": f"Gain set to {gain:.2f}"})
    except Exception as e:
        return error_response(str(e), 400)


@camera_bp.route("/api/camera/zoom", methods=["POST"])
def set_zoom():
    """Set camera zoom level"""
    picam2 = get_camera()
    lock = get_lock()

    print("Setting zoom level...")

    if picam2 is None:
        return jsonify({"success": False, "message": "Camera not available"}), 503

    try:
        zoom_level = float(request.args.get("level", 1.0))
        zoom_level = max(1.0, min(zoom_level, 4.0))

        size = picam2.camera_properties["PixelArraySize"]
        full_w, full_h = size

        new_w = int(full_w / zoom_level)
        new_h = int(full_h / zoom_level)
        x = (full_w - new_w) // 2
        y = (full_h - new_h) // 2
        crop = (x, y, new_w, new_h)

        with lock:
            picam2.set_controls({"ScalerCrop": crop})

        return jsonify({"success": True, "zoom": zoom_level})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@camera_bp.route("/api/camera/start", methods=["POST"])
@with_camera
def start_camera(picam2):
    if not picam2.started:
        picam2.start()
    return jsonify({"success": True, "message": "Camera started"})


@camera_bp.route("/api/camera/stop", methods=["POST"])
@with_camera
def stop_camera(picam2):
    if picam2.started:
        picam2.stop()
    return jsonify({"success": True, "message": "Camera stopped"})


@camera_bp.route("/api/camera/set", methods=["POST"])
@with_camera
def set_camera(picam2):
    data = request.json or {}
    width, height, fps = int(data.get("width", 640)), int(data.get("height", 480)), int(data.get("fps", 30))

    ok, err = validate_camera_settings(width, height, fps)
    if not ok:
        return error_response(err)

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
        return error_response(str(e), 500)


@camera_bp.route("/api/camera/status")
def status():
    picam2 = get_camera()
    if picam2 is None:
        return jsonify({"started": False, "resolution": None, "available": False, "message": "Camera not available"})

    try:
        return jsonify({
            "started": picam2.started,
            "resolution": picam2.camera_configuration()["main"]["size"],
            "available": True
        })
    except Exception as e:
        return error_response(str(e), 500)
